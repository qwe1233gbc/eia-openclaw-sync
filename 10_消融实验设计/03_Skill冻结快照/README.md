# Skill冻结快照

保存通用单项Skill及其哈希。题号只出现在路由表，不写入Skill正文。A/B不加载Skill，C/D按题型只加载一个单项Skill；99汇总Skill不参与单题主生成。


## v2互补性快照

旧版快照原样保留。`skill_snapshots_v2.jsonl`和`skill_hashes_v2.csv`对应程序化Skill：具体法规知识由运行时RAG提供，C组无RAG时安全降级。正式后续运行使用`skill_routing_v2.csv`。
