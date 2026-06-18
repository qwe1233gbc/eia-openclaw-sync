import json, os, re

# Load standard cards
std_path = r"E:\软件\eia-openclaw-sync\03_指南解析_明文标准库\plastic_guide_standard_cards.jsonl"
standards = []
with open(std_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip(): standards.append(json.loads(line))

# Build keyword-to-standard mapping for auto-matching
import collections
std_index = collections.defaultdict(list)
keyword_map = {
    '碘值|碳值|活性炭.*参数|蜂窝|颗粒炭': 'STD_18',
    '活性炭.*更换|更换周期|吸附量|装填': 'STD_19',
    'VOCs.*产生|源强|产污系数|产生量|排放速率': 'STD_11',
    '收集效率|集气罩|控制风速|风量|罩口': 'STD_15',
    '排放标准|DB44|GB315|执行.*标准|特别排放': 'STD_09',
    '总量|分配|削减|替代|减二': 'STD_23',
    '冷却水|排水|废水.*去向|不外排|纳管': 'STD_19',
    '危废|废活性炭|HW49|HW08|固废': 'STD_21',
    '工艺流程|产污节点|产污环节|工艺描述': 'STD_05',
    '原辅材料|MSDS|胶水|胶粘剂|VOCs.*含量|低VOC': 'STD_07',
    '产能|产量.*匹配|物料衡算|设备.*产能': 'STD_08',
    '产品方案|产品.*分类|涂装面积': 'STD_03',
    '附图|附表|一致性|监测计划': 'STD_24',
    '建设内容|项目组成|依托工程': 'STD_01',
    '产业政策|符合性|三线一单': 'STD_01',
    '涂布|复合|涂胶|涂胶量|转移率': 'STD_14',
    '风量.*核算|风机|管道': 'STD_16',
    '危废.*识别|废机油|废油桶|废胶水': 'STD_21',
}

for pattern, std_id in keyword_map.items():
    std_index[pattern] = std_id

def find_best_std(comment_text, location_text):
    """Find the best matching standard card for a comment"""
    combined = (comment_text + ' ' + location_text)
    best_id = None
    best_score = 0
    for pattern, std_id in keyword_map.items():
        matches = re.findall(pattern, combined)
        score = len(matches)
        if score > best_score:
            best_score = score
            best_id = std_id
    return best_id if best_score > 0 else None

def enrich_comment(raw, std_id):
    """Generate enriched comment using standard card template"""
    if not std_id: return None

    # Find the standard card
    std = next((s for s in standards if s['id'] == std_id), None)
    if not std: return None

    raw_text = raw.get('comment_text', '').strip()
    if not raw_text or len(raw_text) < 2 or raw_text in ['同前', '同上', '。', '..']:
        return None

    location = raw.get('location_text', '')[:150]
    section = raw.get('section', '')

    # Build enriched comment
    module = std.get('module', '')
    source = std.get('source', '')
    requirement = std.get('requirement', '')

    enriched = (
        f"【审核模块】{module}\n"
        f"【依据】{source}\n"
        f"【报告原文】{location}\n"
        f"【原始批注】{raw_text}\n"
        f"【标准要求】{requirement}\n"
        f"【升级意见】请对照上述标准要求，补充相应证据材料。原始批注要点：{raw_text}"
    )

    return enriched

# Process all ai_package projects
ai_dir = r"E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\ai_packages_全量"
dst_base = r"E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\升级修改意见_全量"
os.makedirs(dst_base, exist_ok=True)

total_enriched = 0
total_comments = 0
project_count = 0

for proj in sorted(os.listdir(ai_dir)):
    proj_dir = os.path.join(ai_dir, proj)
    if not os.path.isdir(proj_dir): continue

    comments_file = os.path.join(proj_dir, 'comments.jsonl')
    if not os.path.exists(comments_file): continue

    # Read comments
    raw_comments = []
    with open(comments_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try: raw_comments.append(json.loads(line))
                except: pass

    if not raw_comments: continue

    project_count += 1
    total_comments += len(raw_comments)

    # Enrich
    enriched = []
    for c in raw_comments:
        cid = c.get('comment_id', '')
        raw_text = c.get('comment_text', '').strip()
        location_text = c.get('location_text', '')

        std_id = find_best_std(raw_text, location_text)
        enriched_text = enrich_comment(c, std_id)

        if enriched_text:
            enriched.append({
                'comment_id': cid,
                'project': proj[:60],
                'section': c.get('section', ''),
                'original_comment': raw_text,
                'location_text': location_text[:200],
                'linked_standard_card': std_id or 'unmatched',
                'enriched_comment': enriched_text,
                'status': 'AI_enriched_pending_human_review'
            })

    if enriched:
        total_enriched += len(enriched)
        # Save per project
        safe_name = proj[:40].replace('/', '_').replace('\\', '_')
        proj_dst = os.path.join(dst_base, safe_name)
        os.makedirs(proj_dst, exist_ok=True)

        with open(os.path.join(proj_dst, 'enriched_comments.jsonl'), 'w', encoding='utf-8') as f:
            for e in enriched:
                f.write(json.dumps(e, ensure_ascii=False) + '\n')

print(f'Projects processed: {project_count}')
print(f'Total raw comments: {total_comments}')
print(f'Total enriched: {total_enriched}')
print(f'Enrichment rate: {total_enriched/total_comments*100:.0f}%')
print(f'Saved to: {dst_base}')

# Generate summary CSV
import csv
summary_path = os.path.join(dst_base, 'enrichment_summary.csv')
with open(summary_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['project', 'raw_comments', 'enriched', 'enrichment_rate'])
    for proj in sorted(os.listdir(dst_base)):
        proj_dir = os.path.join(dst_base, proj)
        jl = os.path.join(proj_dir, 'enriched_comments.jsonl')
        if os.path.exists(jl):
            with open(jl, 'r', encoding='utf-8') as f2:
                cnt = sum(1 for _ in f2)
            # Find original count
            orig_name = [d for d in os.listdir(ai_dir) if proj[:20] in d]
            orig_cnt = 0
            if orig_name:
                cf = os.path.join(ai_dir, orig_name[0], 'comments.jsonl')
                if os.path.exists(cf):
                    with open(cf, 'r', encoding='utf-8') as f3:
                        orig_cnt = sum(1 for l in f3 if l.strip())
            w.writerow([proj[:40], orig_cnt, cnt, f'{cnt/orig_cnt*100:.0f}%' if orig_cnt else 'N/A'])

print(f'Summary: {summary_path}')
