# A/B/C/D消融实验设计 v2

| 组别 | 共享报告JSON | 冻结RAG | 冻结Skill |
|---|---:|---:|---:|
| A | 有 | 无 | 无 |
| B | 有 | 有 | 无 |
| C | 有 | 无 | 有 |
| D | 有 | 有 | 有 |

强制约束：同题A/B/C/D的`report_context_sha256`相同；同题B/D的`rag_context_sha256`相同；同题C/D的`skill_sha256`相同；D不得获得额外输入。

A、B不调用Skill；C、D只加载题型对应的单项Skill；汇总Skill不参与单题主生成。Qwen不自行选择题目、RAG或Skill，全部输入在模型调用前由程序冻结。
