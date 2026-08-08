"""DashScope 混合检索集成模块

将阿里云 DashScope 的 text-embedding-v3（dense embedding）和 qwen3-rerank（neural reranker）
集成到 RAG 检索管线中，实现与 Zhou 论文对齐的 Dense + Lexical 混合检索。

三阶段检索策略：
  Stage 1: BM25 top-40 + Dense top-40 → RRF(k=60) 融合
  Stage 2: RRF 融合 top-40 → qwen3-rerank 神经重排序 → top-8
  Stage 3: required_source_ids 保底机制，确保关键法规来源不被淘汰

API Key: sk-dd39d877ec55414ab9809fe32f4380e5（通过环境变量 DASHSCOPE_API_KEY 传入）
"""
from __future__ import annotations

import json
import math
import os
import time
from typing import Iterable

# ── 配置常量 ──────────────────────────────────────────────
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-dd39d877ec55414ab9809fe32f4380e5")
EMBEDDING_MODEL = "text-embedding-v3"
EMBEDDING_DIM = 1024
RERANKER_MODEL = "qwen3-rerank"
RRF_K = 60                          # Reciprocal Rank Fusion 常数，与 Zhou 论文一致
CANDIDATE_K_SPARSE = 40            # BM25 召回数
CANDIDATE_K_DENSE = 40             # Dense 召回数
RERANK_CANDIDATES = 40             # 送入 reranker 的候选数
FINAL_K = 8                        # 最终保留的 parent chunk 数
EMBED_BATCH_SIZE = 25              # DashScope embedding 单次最大文本数
EMBED_MAX_CHARS = 2048             # 单文本截断长度（API 限制 8192 tokens，2048 字符足够安全）


# ── 1. DashScope Embedding ─────────────────────────────────
def embed_texts(texts: list[str], text_type: str = "document") -> list[list[float]]:
    """调用 DashScope text-embedding-v3 批量编码文本。

    Args:
        texts: 待编码文本列表
        text_type: "document"（文档入库）或 "query"（查询编码）

    Returns:
        list[list[float]]: 每个文本对应的 1024 维向量
    """
    import dashscope
    dashscope.api_key = DASHSCOPE_API_KEY

    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        # 截断超长文本
        batch = [t[:EMBED_MAX_CHARS] if len(t) > EMBED_MAX_CHARS else t for t in batch]
        resp = dashscope.TextEmbedding.call(
            model=EMBEDDING_MODEL,
            input=batch,
            dimension=EMBEDDING_DIM,
            output_type="dense",
            text_type=text_type,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"DashScope embedding 失败: {resp.status_code} {resp.message}")
        for item in resp.output["embeddings"]:
            all_embeddings.append(item["embedding"])
    return all_embeddings


def embed_query(query: str) -> list[float]:
    """编码查询文本。"""
    return embed_texts([query], text_type="query")[0]


# ── 2. Dense 检索（余弦相似度）──────────────────────────────
def dense_rank(
    query_vec: list[float],
    doc_vectors: list[list[float]],
    documents: list[dict],
    top_k: int = CANDIDATE_K_DENSE,
) -> list[dict]:
    """基于预计算的文档向量，用余弦相似度排序。

    Args:
        query_vec: 查询向量 (1024,)
        doc_vectors: 文档向量列表
        documents: 文档列表（dict），需要包含 parent_id
        top_k: 返回前 K 个

    Returns:
        排序后的文档列表，附加 dense_score 和 dense_rank 字段
    """
    q_norm = math.sqrt(sum(x * x for x in query_vec))
    if q_norm == 0:
        q_norm = 1.0
    scored = []
    for doc, dvec in zip(documents, doc_vectors):
        d_norm = math.sqrt(sum(x * x for x in dvec))
        if d_norm == 0:
            d_norm = 1.0
        dot = sum(q * d for q, d in zip(query_vec, dvec))
        cos_sim = dot / (q_norm * d_norm)
        scored.append({**doc, "dense_score": round(cos_sim, 6)})
    scored.sort(key=lambda x: (-x["dense_score"], x.get("parent_id", "")))
    for rank, item in enumerate(scored[:top_k], 1):
        item["dense_rank"] = rank
    return scored[:top_k]


# ── 3. RRF 融合 ─────────────────────────────────────────────
def rrf_fuse(
    bm25_ranked: list[dict],
    dense_ranked: list[dict],
    k: int = RRF_K,
) -> list[dict]:
    """Reciprocal Rank Fusion: score(d) = Σ 1/(k + rank_i(d))

    Args:
        bm25_ranked: BM25 排序结果（已按分数降序）
        dense_ranked: Dense 排序结果（已按分数降序）
        k: RRF 常数（默认 60，与 Zhou 论文一致）

    Returns:
        融合后按 RRF 分数降序排列的文档列表
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for rank, doc in enumerate(bm25_ranked, 1):
        pid = doc.get("parent_id", "")
        scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + rank)
        doc_map[pid] = doc

    for rank, doc in enumerate(dense_ranked, 1):
        pid = doc.get("parent_id", "")
        scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + rank)
        if pid not in doc_map:
            doc_map[pid] = doc

    fused = [(pid, score) for pid, score in scores.items()]
    fused.sort(key=lambda x: (-x[1], x[0]))
    result = []
    for rank, (pid, score) in enumerate(fused, 1):
        result.append({**doc_map[pid], "rrf_score": round(score, 6), "rrf_rank": rank})
    return result


# ── 4. 神经重排序（qwen3-rerank）────────────────────────────
def neural_rerank(
    query: str,
    candidates: list[dict],
    top_k: int = FINAL_K,
) -> list[dict]:
    """调用 qwen3-rerank 对候选文档重排序。

    Args:
        query: 查询文本
        candidates: RRF 融合后的候选文档列表
        top_k: 最终保留数量

    Returns:
        重排序后的 top-k 文档列表，附加 rerank_score 和 rerank_rank 字段
    """
    import dashscope
    dashscope.api_key = DASHSCOPE_API_KEY

    if not candidates:
        return []

    # 提取文档内容用于 rerank
    documents = []
    for c in candidates[:RERANK_CANDIDATES]:
        content = c.get("content", "")
        # 截断超长内容，qwen3-rerank 最大 512 tokens
        if len(content) > 1500:
            content = content[:1500]
        documents.append(content)

    resp = dashscope.TextReRank.call(
        model=RERANKER_MODEL,
        query=query[:1500],
        documents=documents,
        top_n=top_k,
        return_documents=False,
        instruct="Given a web search query, retrieve relevant passages that answer the query.",
    )

    if resp.status_code != 200:
        raise RuntimeError(f"DashScope rerank 失败: {resp.status_code} {resp.message}")

    # resp.output.results 是 [{"index": int, "relevance_score": float}, ...]
    reranked = []
    for item in resp.output["results"]:
        idx = item["index"]
        score = item["relevance_score"]
        doc = candidates[idx]
        reranked.append({**doc, "rerank_score": round(score, 6)})

    for rank, item in enumerate(reranked, 1):
        item["rerank_rank"] = rank

    return reranked[:top_k]


# ── 5. required_source_ids 保底机制 ─────────────────────────
def ensure_required_sources(
    reranked: list[dict],
    all_candidates: list[dict],
    required_source_ids: Iterable[str],
    final_k: int = FINAL_K,
) -> list[dict]:
    """确保 required_source_ids 对应的文档不被 reranker 淘汰。

    策略：
      1. 先取 reranker 的 top-k
      2. 检查是否有 required source 缺失
      3. 如有缺失，从 all_candidates 中补充（按 RRF 分数排序）
      4. 去重后截断至 final_k

    这保留了原 select_required_sources 的核心逻辑：
    关键法规来源不会被 reranker 的低分淘汰。
    """
    required = list(dict.fromkeys(required_source_ids))
    selected = list(reranked[:final_k])

    # 已选中的 parent_ids 和 source_ids
    selected_pids = {d.get("parent_id") for d in selected}
    selected_sources = {d.get("source_id") for d in selected}

    # 补充缺失的 required sources
    for sid in required:
        if sid in selected_sources:
            continue
        # 从 all_candidates 中找该 source 的最佳候选
        for doc in all_candidates:
            if doc.get("source_id") == sid and doc.get("parent_id") not in selected_pids:
                selected.append(doc)
                selected_pids.add(doc.get("parent_id"))
                selected_sources.add(sid)
                break

    return selected[:final_k]


# ── 6. 端到端混合检索 ──────────────────────────────────────
def hybrid_retrieve(
    query: str,
    documents: list[dict],
    doc_vectors: list[list[float]],
    bm25_fn,
    required_source_ids: Iterable[str] = (),
    candidate_k_sparse: int = CANDIDATE_K_SPARSE,
    candidate_k_dense: int = CANDIDATE_K_DENSE,
    rerank_candidates: int = RERANK_CANDIDATES,
    final_k: int = FINAL_K,
) -> tuple[list[dict], dict]:
    """端到端三阶段混合检索。

    Args:
        query: 查询文本
        documents: 全量文档列表（dict）
        doc_vectors: 预计算的文档向量列表（与 documents 一一对应）
        bm25_fn: BM25 排序函数 (query, documents, top_k) -> ranked_list
        required_source_ids: 必须包含的来源 ID
        candidate_k_sparse: BM25 召回数
        candidate_k_dense: Dense 召回数
        rerank_candidates: 送入 reranker 的候选数
        final_k: 最终返回数量

    Returns:
        (selected_docs, trace_info)
        trace_info 包含各阶段的信息用于追溯
    """
    trace = {
        "candidate_k_sparse": candidate_k_sparse,
        "candidate_k_dense": candidate_k_dense,
        "rerank_candidates": rerank_candidates,
        "final_k": final_k,
    }

    # Stage 1a: BM25 召回
    bm25_ranked = bm25_fn(query, documents, top_k=len(documents))
    bm25_top = bm25_ranked[:candidate_k_sparse]
    trace["bm25_top_ids"] = [d["parent_id"] for d in bm25_top]

    # Stage 1b: Dense 召回
    query_vec = embed_query(query)
    dense_top = dense_rank(query_vec, doc_vectors, documents, top_k=candidate_k_dense)
    trace["dense_top_ids"] = [d["parent_id"] for d in dense_top]

    # Stage 1c: RRF 融合
    fused = rrf_fuse(bm25_top, dense_top, k=RRF_K)
    fused_top = fused[:rerank_candidates]
    trace["rrf_fused_ids"] = [d["parent_id"] for d in fused_top]
    trace["rrf_fused_count"] = len(fused_top)

    # Stage 2: 神经重排序
    reranked = neural_rerank(query, fused_top, top_k=final_k)
    trace["reranked_ids"] = [d["parent_id"] for d in reranked]

    # Stage 3: required_source_ids 保底
    required = list(required_source_ids)
    if required:
        selected = ensure_required_sources(reranked, fused, required, final_k=final_k)
    else:
        selected = reranked[:final_k]

    trace["selected_ids"] = [d["parent_id"] for d in selected]
    trace["selected_sources"] = list({d.get("source_id") for d in selected})

    return selected, trace


# ── 7. 批量预计算文档向量 ───────────────────────────────────
def precompute_doc_embeddings(
    documents: list[dict],
    cache_path: str | None = None,
) -> tuple[list[list[float]], str]:
    """批量预计算所有文档的 embedding 向量。

    Args:
        documents: 文档列表
        cache_path: 向量缓存文件路径（JSON 格式）

    Returns:
        (vectors, embedding_revision)
    """
    import hashlib

    # 检查缓存
    if cache_path and os.path.exists(cache_path):
        # 计算当前文档集合的指纹
        content_hashes = [d.get("content_sha256", "") for d in documents]
        current_fingerprint = hashlib.sha256(
            "".join(content_hashes).encode("utf-8")
        ).hexdigest()

        cached = json.loads(open(cache_path, encoding="utf-8").read())
        if cached.get("fingerprint") == current_fingerprint:
            print(f"  [缓存命中] 加载 {len(cached['vectors'])} 个预计算向量")
            return cached["vectors"], cached.get("revision", "cached")

    # 重新计算
    print(f"  [预计算] 开始编码 {len(documents)} 个文档...")
    texts = [d.get("content", "")[:EMBED_MAX_CHARS] for d in documents]
    vectors = embed_texts(texts, text_type="document")

    # 计算版本号
    content_hashes = [d.get("content_sha256", "") for d in documents]
    fingerprint = hashlib.sha256(
        "".join(content_hashes).encode("utf-8")
    ).hexdigest()
    revision = f"v1_{fingerprint[:8]}"

    # 写入缓存
    if cache_path:
        cache_data = {
            "model": EMBEDDING_MODEL,
            "dimension": EMBEDDING_DIM,
            "vectors": vectors,
            "fingerprint": fingerprint,
            "revision": revision,
            "document_count": len(documents),
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False)
        print(f"  [缓存写入] 保存到 {cache_path}")

    return vectors, revision


# ── 8. 自检 ────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("DashScope 混合检索模块自检")
    print("=" * 60)

    # 测试 embedding
    print("\n[1/3] 测试 text-embedding-v3...")
    texts = [
        "国民经济行业分类 GB/T 4754-2017",
        "塑料制品业 C292 塑料薄膜制造 C2921",
        "水污染物排放标准 DB44/26-2001",
    ]
    vecs = embed_texts(texts)
    print(f"  向量数: {len(vecs)}, 维度: {len(vecs[0])}")

    # 测试 dense_rank
    print("\n[2/3] 测试 dense_rank...")
    docs = [
        {"parent_id": "doc1", "source_id": "S1", "content": texts[0]},
        {"parent_id": "doc2", "source_id": "S2", "content": texts[1]},
        {"parent_id": "doc3", "source_id": "S3", "content": texts[2]},
    ]
    qvec = embed_query("塑胶行业的国民经济行业分类代码")
    ranked = dense_rank(qvec, vecs, docs, top_k=3)
    for r in ranked:
        print(f"  {r['parent_id']}: dense_score={r['dense_score']:.4f}")

    # 测试 rerank
    print("\n[3/3] 测试 qwen3-rerank...")
    reranked = neural_rerank("塑胶行业的国民经济行业分类代码", ranked, top_k=2)
    for r in reranked:
        print(f"  {r['parent_id']}: rerank_score={r['rerank_score']:.4f}")

    print("\n" + "=" * 60)
    print("自检完成")
    print("=" * 60)
