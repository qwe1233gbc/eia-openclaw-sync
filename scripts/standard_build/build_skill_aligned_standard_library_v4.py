import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STD_DIR = ROOT / "03_指南解析_明文标准库"
INPUT_JSONL = STD_DIR / "plastic_guide_standard_library_v3_deep.jsonl"
OUT_JSONL = STD_DIR / "plastic_guide_standard_library_v4_skill_aligned_pilot.jsonl"
OUT_MD = STD_DIR / "plastic_guide_standard_library_v4_skill_aligned_pilot.md"
OUT_REPORT_CSV = STD_DIR / "standard_reference_pilot_from_reports.csv"
OUT_MANIFEST = STD_DIR / "standard_source_download_manifest_v4.md"


OFFICIAL_SOURCES = {
    "GB/T 4754-2017": {
        "title": "国民经济行业分类",
        "url": "https://www.stats.gov.cn/xxgk/tjbz/gjtjbz/201710/t20171017_1758922.html",
        "local_note": "国家统计局页面含 docx/pdf 附件；本次先使用仓库内已校正分类 JSON/JSONL。",
    },
    "HJ 1122-2020": {
        "title": "排污许可证申请与核发技术规范 橡胶和塑料制品工业",
        "url": "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/pwxk/202004/W020200401327032592051.pdf",
        "local_note": "已下载到 03_指南解析_明文标准库/_source_downloads_v4/HJ_1122-2020.pdf，PDF 不提交。",
    },
    "GB 37822-2019": {
        "title": "挥发性有机物无组织排放控制标准",
        "url": "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqgdwrywrwpfbz/201906/W020190606587693632696.pdf",
        "local_note": "已下载到 03_指南解析_明文标准库/_source_downloads_v4/GB_37822-2019.pdf，PDF 不提交。",
    },
    "GB 31572-2015": {
        "title": "合成树脂工业污染物排放标准（含 2024 修改内容）",
        "url": "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqgdwrywrwpfbz/201505/W020240612354056402310.pdf",
        "local_note": "已下载到 03_指南解析_明文标准库/_source_downloads_v4/GB_31572-2015_2024_modified.pdf，PDF 不提交。",
    },
}


def ref(std, clause="", text="", url=""):
    return {"std": std, "clause": clause, "text": text, "source_url": url}


def entry(module, source_file, source_section, requirement, skill_id, skill_name,
          trigger, evidence, refs, notes="", source_type="standard_file",
          source_page_or_table="", status="manual_check_needed"):
    return {
        "module": module,
        "source_type": source_type,
        "source_file": source_file,
        "source_section": source_section,
        "source_page_or_table": source_page_or_table,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "trigger": trigger if isinstance(trigger, list) else [trigger],
        "requirement": requirement,
        "check_evidence": evidence if isinstance(evidence, list) else [evidence],
        "notes": notes,
        "standard_refs": refs,
        "review_status": status,
        "entry_origin": "v4_skill_aligned_pilot",
    }


SKILL_ENTRIES = [
    # 01 industry classification
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C292",
          "行业类别审核应先判断项目是否属于 C292 塑料制品业，再下钻至 C2921-C2929 小类；不得仅因存在注塑设备就默认写为 C2929。",
          "01", "国民经济行业类别审核", "报告行业类别笼统写 C2929 或与产品不一致",
          ["建设项目行业类别章节", "产品方案", "生产工艺", "主要原辅材料"],
          [ref("GB/T 4754-2017", "C292", "塑料制品业小类划分", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2921",
          "产品为塑料薄膜、包装薄膜、功能薄膜时，应优先核对是否属于 C2921 塑料薄膜制造，而不是直接归入 C2929。",
          "01", "国民经济行业类别审核", "产品含塑料薄膜但行业写为其他塑料制品",
          ["产品名称", "产品用途", "生产工艺", "产能"],
          [ref("GB/T 4754-2017", "C2921", "塑料薄膜制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2922",
          "产品为塑料板、管、型材、片材、管件等时，应核对 C2922 塑料板、管、型材制造。",
          "01", "国民经济行业类别审核", "塑料板管型材项目行业类别不清",
          ["产品方案", "规格型号", "工艺流程"],
          [ref("GB/T 4754-2017", "C2922", "塑料板、管、型材制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2923",
          "产品为塑料丝、绳、编织袋、编织布等时，应核对 C2923 塑料丝、绳及编织品制造。",
          "01", "国民经济行业类别审核", "编织袋/编织布项目行业类别不清",
          ["产品方案", "原料树脂", "拉丝/编织工艺"],
          [ref("GB/T 4754-2017", "C2923", "塑料丝、绳及编织品制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2924",
          "涉及发泡成型、泡沫板、泡沫包装材料等产品时，应核对 C2924 泡沫塑料制造。",
          "01", "国民经济行业类别审核", "发泡产品未识别为泡沫塑料制造",
          ["产品名称", "发泡工艺", "原辅材料"],
          [ref("GB/T 4754-2017", "C2924", "泡沫塑料制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2925",
          "产品为塑料人造革、合成革时，应核对 C2925，并重点关注涂布、复合、溶剂或胶粘剂使用。",
          "01", "国民经济行业类别审核", "人造革/合成革项目未识别复合涂布属性",
          ["产品方案", "涂布/复合工艺", "胶粘剂或溶剂清单"],
          [ref("GB/T 4754-2017", "C2925", "塑料人造革、合成革制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2926",
          "产品为塑料包装箱、塑料容器、瓶、桶等时，应核对 C2926 塑料包装箱及容器制造。",
          "01", "国民经济行业类别审核", "塑料包装箱/容器项目行业小类不清",
          ["产品名称", "用途", "吹塑/注塑/吸塑工艺"],
          [ref("GB/T 4754-2017", "C2926", "塑料包装箱及容器制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2927",
          "产品为日用塑料制品时，应核对 C2927；若为工业配套零部件则不宜直接归入日用塑料制品。",
          "01", "国民经济行业类别审核", "日用塑料与工业塑料零件混用",
          ["产品用途", "客户行业", "产品方案"],
          [ref("GB/T 4754-2017", "C2927", "日用塑料制品制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2928",
          "产品为人造草坪时，应核对 C2928，并关注背胶、复合或涂胶环节是否触发 VOCs 审核。",
          "01", "国民经济行业类别审核", "人造草坪项目未识别背胶/复合环节",
          ["产品方案", "背胶工艺", "胶粘剂清单"],
          [ref("GB/T 4754-2017", "C2928", "人造草坪制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C2929",
          "C2929 仅适用于未列明的塑料零件及其他塑料制品；若产品可归入 C2921-C2928，应优先采用更具体小类。",
          "01", "国民经济行业类别审核", "报告默认 C2929 但产品有更具体小类",
          ["产品方案", "产品用途", "行业类别说明"],
          [ref("GB/T 4754-2017", "C2929", "塑料零件及其他塑料制品制造", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),
    entry("国民经济行业分类", "GB/T 4754-2017 国民经济行业分类", "C291/C2651/C4220",
          "橡胶制品、初级形态塑料及合成树脂、废塑料回收分选再加工等相邻行业不得简单归入 C292 塑料制品业。",
          "01", "国民经济行业类别审核", "橡胶、树脂制造或废塑料再生项目被误归入 C292",
          ["原料来源", "最终产品", "是否发生聚合/改性造粒/回收分选"],
          [ref("GB/T 4754-2017", "C291/C2651/C4220", "相邻行业边界", OFFICIAL_SOURCES["GB/T 4754-2017"]["url"])]),

    # 02 investment
    entry("环保投资核算", "建设项目环境影响报告表编制技术指南（污染影响类）", "建设内容/环保工程",
          "环保投资应能与废气、废水、噪声、固废、风险防控等治理措施逐项对应，不能只给总额而无分项。",
          "02", "环评投资核算审核", "环保投资只列总额或与治理措施不对应",
          ["环保投资表", "污染防治措施章节", "工程组成表"],
          [ref("建设项目环境影响报告表编制技术指南（污染影响类）", "工程内容", "环保工程和投资应与治理措施对应")]),
    entry("环保投资核算", "佛山市塑胶行业环评编制指南（试行）", "工程分析/治理措施",
          "涉 VOCs 项目应核对废气收集、治理设施、危废暂存、监测等环保投资是否纳入项目总投资。",
          "02", "环评投资核算审核", "涉 VOCs 治理设施未计入环保投资",
          ["项目总投资", "环保投资明细", "废气治理设施清单"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "工程分析", "塑胶项目应说明废气治理和环保工程配置")]),

    # 03 three lines one list
    entry("三线一单", "顺德区三线一单管控单元准入清单", "管控单元匹配",
          "顺德区项目应写明所在环境管控单元编码、单元名称和管控类型，并逐项对照空间布局、污染物排放、环境风险和资源利用要求。",
          "03", "三线一单符合性审核", "三线一单只作概括性描述",
          ["项目地理位置", "管控单元编码", "准入清单对照表"],
          [ref("佛山市顺德区三线一单生态环境分区管控方案", "准入清单", "顺德区环境管控单元要求")]),
    entry("三线一单", "广东省/佛山市/顺德区三线一单文件", "三级对照",
          "报告应分别核对广东省、佛山市和顺德区三级三线一单要求，不能只引用其中一级。",
          "03", "三线一单符合性审核", "缺少省/市/区任一级三线一单对照",
          ["三线一单章节", "省市区对照表", "管控单元截图"],
          [ref("三线一单生态环境分区管控方案", "省/市/区", "三级管控要求")]),
    entry("三线一单", "三线一单管控要求", "VOCs 管控",
          "涉 VOCs 项目应核对低 VOCs 原辅材料替代、无组织排放控制、低效治理设施淘汰和总量替代等管控要求。",
          "03", "三线一单符合性审核", "三线一单未结合 VOCs 管控要求",
          ["原辅材料 VOCs 含量", "废气治理工艺", "总量控制说明"],
          [ref("三线一单生态环境分区管控方案", "污染物排放管控", "涉 VOCs 项目管控要求")]),

    # 04 construction completeness
    entry("建设内容完整性", "建设项目环境影响报告表编制技术指南（污染影响类）", "工程组成",
          "工程组成应区分主体工程、辅助工程、公用工程、环保工程、储运工程和依托工程。",
          "04", "建设内容完整性审核", "工程组成缺项或类别混乱",
          ["工程组成表", "平面布置图", "依托工程说明"],
          [ref("建设项目环境影响报告表编制技术指南（污染影响类）", "建设内容", "工程组成完整性要求")]),
    entry("建设内容完整性", "佛山市塑胶行业环评编制指南（试行）", "产品方案",
          "涉涂胶、复合、印刷、熟化项目的产品方案应补充面积、层数、复合结构或对应生产批次等能支撑 VOCs 核算的参数。",
          "04", "建设内容完整性审核", "产品方案无法支撑 VOCs 或胶水用量核算",
          ["产品方案表", "涂布/复合面积", "产能匹配说明"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "产品方案", "涉胶水/复合项目产品参数要求")]),
    entry("建设内容完整性", "佛山市塑胶行业环评编制指南（试行）", "原辅材料",
          "含 VOCs 原辅材料应列明名称、年用量、最大储存量、VOCs 含量来源、MSDS 或检测报告、包装和储存位置。",
          "04", "建设内容完整性审核", "原辅材料表缺 VOCs 含量或 MSDS 来源",
          ["原辅材料表", "MSDS", "检测报告", "储存位置图"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "原辅材料", "含 VOCs 原辅材料证据要求")]),
    entry("建设内容完整性", "佛山市塑胶行业环评编制指南（试行）", "生产设备",
          "生产设备表应列明设备名称、数量、型号、关键参数，并与产能、工序和污染源识别相互匹配。",
          "04", "建设内容完整性审核", "设备表无法支撑产能或源强核算",
          ["设备清单", "设备参数", "工艺流程图"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "设备清单", "设备与产能匹配要求")]),
    entry("建设内容完整性", "佛山市塑胶行业环评编制指南（试行）", "工艺流程",
          "工艺流程图应覆盖投料、混合、涂胶/复合/熟化、印刷、热熔/挤出、破碎、清洗等全部产污节点。",
          "04", "建设内容完整性审核", "工艺流程遗漏产污节点",
          ["工艺流程图", "产污环节表", "设备布置"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "工艺流程", "产污节点识别要求")]),

    # 05/06 environmental quality and quality standards
    entry("环境质量现状", "GB 3095-2012 环境空气质量标准", "二类区",
          "报告应说明项目所在地环境空气功能区类别，并核对区域达标情况；臭氧等超标因子应说明改善计划或区域达标规划。",
          "05", "环境质量现状数据审核", "环境空气质量现状引用不完整",
          ["环境空气功能区", "年度环境质量公报", "达标区判定"],
          [ref("GB 3095-2012", "环境空气质量功能区", "二类区环境空气质量评价")]),
    entry("环境质量现状", "GB 3838-2002 地表水环境质量标准", "水功能区",
          "涉及受纳水体时，应核对水环境功能区和执行类别，说明引用监测断面与项目排水去向的关系。",
          "05", "环境质量现状数据审核", "地表水断面或执行类别不清",
          ["受纳水体", "水功能区划", "监测断面"],
          [ref("GB 3838-2002", "地表水类别", "水环境质量评价")]),
    entry("环境质量执行标准", "GB 3096-2008 声环境质量标准", "声环境功能区",
          "声环境现状评价应先确定声功能区类别，再选择相应标准限值；工业区常见为 3 类，但需以功能区划为准。",
          "06", "环境质量执行标准审核", "声环境类别凭经验填写",
          ["声功能区划", "项目位置", "厂界周边敏感点"],
          [ref("GB 3096-2008", "声环境功能区", "声环境质量标准类别")]),
    entry("环境质量执行标准", "GB 12348-2008 工业企业厂界环境噪声排放标准", "厂界噪声",
          "厂界噪声排放标准应与声功能区类别一致，并区分昼间、夜间限值。",
          "06", "环境质量执行标准审核", "厂界噪声排放标准类别错误",
          ["声功能区划", "厂界噪声预测", "执行标准表"],
          [ref("GB 12348-2008", "厂界噪声", "工业企业厂界环境噪声排放限值")]),

    # 07 emission standards
    entry("污染物排放标准", "GB 31572-2015 合成树脂工业污染物排放标准", "塑料制品参照执行",
          "塑料制品工业企业及其生产设施可参照 GB 31572 执行；报告应说明适用理由、污染因子和对应表号。",
          "07", "污染物排放标准审核", "塑料制品废气标准适用理由不清",
          ["行业类别", "生产工艺", "执行标准表", "污染因子"],
          [ref("GB 31572-2015", "适用范围", "塑料制品工业企业及其生产设施参照执行", OFFICIAL_SOURCES["GB 31572-2015"]["url"])]),
    entry("污染物排放标准", "GB 31572-2015 合成树脂工业污染物排放标准", "有组织废气",
          "热熔、挤出、注塑、造粒等塑料加工废气的非甲烷总烃、颗粒物等因子，应核对 GB 31572 对应表格或与地方标准取严。",
          "07", "污染物排放标准审核", "有组织废气限值未说明取严关系",
          ["废气排放口", "污染因子", "执行标准限值", "取严比较表"],
          [ref("GB 31572-2015", "大气污染物排放限值", "有组织排放限值", OFFICIAL_SOURCES["GB 31572-2015"]["url"])]),
    entry("污染物排放标准", "GB 31572-2015 合成树脂工业污染物排放标准", "企业边界",
          "无组织非甲烷总烃、颗粒物等边界排放限值应核对 GB 31572 企业边界要求，并与 DB44/2367、DB44/27 等地方标准取严。",
          "07", "污染物排放标准审核", "无组织废气边界标准漏项",
          ["无组织排放源", "厂界监控点", "执行标准表"],
          [ref("GB 31572-2015", "企业边界", "企业边界排放限值", OFFICIAL_SOURCES["GB 31572-2015"]["url"])]),
    entry("污染物排放标准", "GB 37822-2019 挥发性有机物无组织排放控制标准", "VOCs 无组织控制",
          "含 VOCs 物料储存、转移输送、工艺过程和废气收集处理系统应按 GB 37822 核对无组织控制要求。",
          "07", "污染物排放标准审核", "只列排放限值但未核对无组织控制措施",
          ["含 VOCs 物料储存方式", "转移输送方式", "废气收集系统", "厂区内监测要求"],
          [ref("GB 37822-2019", "控制要求", "VOCs 无组织排放控制", OFFICIAL_SOURCES["GB 37822-2019"]["url"])]),
    entry("污染物排放标准", "DB44/2367-2022 固定污染源挥发性有机物综合排放标准", "厂区内 VOCs",
          "广东省项目应核对 DB44/2367 对厂区内 VOCs 无组织排放限值和监控要求。",
          "07", "污染物排放标准审核", "厂区内 VOCs 标准遗漏",
          ["厂区内监控点", "NMHC 限值", "执行标准表"],
          [ref("DB44/2367-2022", "厂区内 VOCs", "固定污染源挥发性有机物综合排放标准")]),
    entry("污染物排放标准", "GB 14554-93 恶臭污染物排放标准", "臭气浓度",
          "热熔、挤出、橡胶或含异味工序涉及臭气浓度时，应核对 GB 14554 有组织和厂界限值。",
          "07", "污染物排放标准审核", "臭气浓度未纳入执行标准",
          ["产臭工序", "有组织排口", "厂界监控点"],
          [ref("GB 14554-93", "臭气浓度", "恶臭污染物排放限值")]),
    entry("污染物排放标准", "DB44/26-2001 水污染物排放限值", "生活污水/生产废水",
          "生活污水或生产废水进入市政管网、园区污水站或直接外排时，应核对纳管或外排执行标准。",
          "07", "污染物排放标准审核", "废水去向与执行标准不匹配",
          ["排水去向", "污水站接收证明", "废水执行标准"],
          [ref("DB44/26-2001", "第二时段", "广东省水污染物排放限值")]),

    # 08/09 source coefficients
    entry("产污系数适用性", "292 塑料制品业产污系数手册", "废气系数",
          "采用产污系数法时，应核对产品、原料、工艺、规模和污染物因子是否落入系数手册适用范围。",
          "08", "产污系数适用性审核", "直接套用系数但未说明适用条件",
          ["产品类别", "工艺", "原辅材料", "系数手册条目"],
          [ref("292 塑料制品业产污系数手册", "废气", "产污系数适用范围")]),
    entry("产污系数适用性", "HJ 1122-2020", "附录 G",
          "排污许可或源强核算涉及塑料制品工业产污系数时，可参考 HJ 1122 附录 G，并与报告采用的系数来源一致性核对。",
          "08", "产污系数适用性审核", "系数来源与行业/工艺不一致",
          ["系数来源", "工艺类型", "污染因子"],
          [ref("HJ 1122-2020", "附录 G", "橡胶和塑料制品工业污染物产污系数表", OFFICIAL_SOURCES["HJ 1122-2020"]["url"])]),
    entry("源强定量核算", "佛山市塑胶行业环评编制指南（试行）", "VOCs 源强",
          "VOCs 源强核算应说明采用物料衡算法、产污系数法或实测类比法的原因，并列出计算过程。",
          "09", "源强定量核算审核", "只给排放量结果不列计算过程",
          ["源强核算表", "VOCs 含量", "用量", "收集效率", "处理效率"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "工程分析", "VOCs 源强核算要求")]),
    entry("源强定量核算", "佛山市塑胶行业环评编制指南（试行）", "胶粘剂用量",
          "胶粘剂用量应与产品面积、涂布量、转移率、胶水浓度、设备产能等参数相互校核。",
          "09", "源强定量核算审核", "胶水用量与产品面积或设备产能不匹配",
          ["胶水用量", "涂布面积", "设备参数", "产品方案"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "附录/表格", "胶粘剂用量核算")]),
    entry("源强定量核算", "GB 33372-2020 胶粘剂 VOCs 限量", "胶粘剂 VOCs",
          "胶粘剂 VOCs 含量应依据 MSDS、检测报告或产品标准核对，并与低 VOCs 判定、源强核算使用值一致。",
          "09", "源强定量核算审核", "MSDS VOCs 含量与源强计算值不一致",
          ["MSDS", "检测报告", "源强核算表"],
          [ref("GB 33372-2020", "胶粘剂 VOCs 限量", "胶粘剂中 VOCs 含量限值")]),

    # 10/11/12 gas collection and airflow
    entry("废气收集形式", "GB 37822-2019", "收集处理系统",
          "产生 VOCs 的工序应优先在密闭空间或设备中进行；无法密闭的，应采取局部收集并说明控制风速、收集范围和无组织控制措施。",
          "10", "废气收集形式审核", "VOCs 工序仅写集气罩但无收集合理性说明",
          ["工艺设备", "密闭方式", "集气罩设置", "车间平面图"],
          [ref("GB 37822-2019", "VOCs 废气收集处理系统", "收集系统控制要求", OFFICIAL_SOURCES["GB 37822-2019"]["url"])]),
    entry("废气收集形式", "GB/T 16758 排风罩的分类及技术条件", "集气罩",
          "采用集气罩收集时，应说明罩型、罩口尺寸、污染源距离和控制风速，避免只有收集效率结论。",
          "10", "废气收集形式审核", "集气罩参数缺失",
          ["集气罩示意图", "罩口尺寸", "控制风速", "设备布置"],
          [ref("GB/T 16758", "排风罩", "排风罩分类和技术条件")]),
    entry("废气设计风量", "AQ/T 4274 局部排风设施控制风速检测与评估技术规范", "控制风速",
          "设计风量应由罩口面积、控制风速、同时运行数量等参数计算，不宜只按经验值填写。",
          "11", "废气设计风量审核", "风量缺少计算依据",
          ["罩口面积", "控制风速", "设备数量", "同时运行系数"],
          [ref("AQ/T 4274", "控制风速", "局部排风设施控制风速检测与评估")]),
    entry("废气设计风量", "佛山市塑胶行业环评编制指南（试行）", "风量核算",
          "报告应核对设计风量与治理设施处理能力、排气筒排放量和收集系统阻力是否匹配。",
          "11", "废气设计风量审核", "设计风量与治理设施能力不匹配",
          ["风量计算表", "风机参数", "治理设施设计参数"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "废气收集", "风量核算要求")]),
    entry("废气收集效率", "佛山市塑胶行业环评编制指南（试行）", "收集效率",
          "废气收集效率应根据收集形式、密闭程度、罩口距离、控制风速等条件取值；不得无依据套用高效率。",
          "12", "废气收集效率审核", "收集效率取值过高或无依据",
          ["收集形式", "密闭条件", "控制风速", "效率取值依据"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "废气收集效率", "收集效率取值条件")]),
    entry("废气收集效率", "GB 37822-2019", "无组织排放控制",
          "收集效率不能只作为源强计算参数，还应与无组织排放控制措施、厂区内监控要求相互印证。",
          "12", "废气收集效率审核", "收集效率与无组织控制措施脱节",
          ["源强核算", "无组织控制措施", "厂区内监测计划"],
          [ref("GB 37822-2019", "无组织排放控制", "VOCs 无组织排放控制", OFFICIAL_SOURCES["GB 37822-2019"]["url"])]),

    # 13 activated carbon
    entry("活性炭参数", "HJ 2026-2013 吸附法工业有机废气治理工程技术规范", "吸附装置",
          "采用活性炭吸附时，应列明活性炭类型、装填量、碘值或吸附性能、空塔气速、停留时间和更换周期。",
          "13", "活性炭参数审核", "活性炭只写二级吸附但参数缺失",
          ["活性炭装填量", "碘值/性能参数", "设计风量", "更换周期"],
          [ref("HJ 2026-2013", "吸附法治理工程", "活性炭吸附装置设计和运行参数")]),
    entry("活性炭参数", "佛山市塑胶行业环评编制指南（试行）", "活性炭更换周期",
          "活性炭更换周期应结合 VOCs 削减量、活性炭吸附容量、装填量和运行时间计算或说明，不宜只写定期更换。",
          "13", "活性炭参数审核", "活性炭更换周期无计算依据",
          ["VOCs 削减量", "装填量", "吸附容量", "运行时间", "更换频次"],
          [ref("佛山市塑胶行业环评编制指南（试行）", "活性炭管理", "活性炭更换周期核算")]),
    entry("活性炭参数", "HJ 1122-2020", "污染防治可行技术",
          "活性炭吸附作为治理措施时，应核对其是否属于相应产污环节的可行技术，并说明运行维护要求。",
          "13", "活性炭参数审核", "治理工艺可行性未说明",
          ["产污环节", "治理工艺", "运行维护制度"],
          [ref("HJ 1122-2020", "污染防治可行技术", "塑料制品工业污染防治可行技术", OFFICIAL_SOURCES["HJ 1122-2020"]["url"])]),

    # 14 hazardous waste
    entry("危险废物识别", "国家危险废物名录", "废活性炭/废机油/废包装",
          "危险废物识别应结合产生环节、沾染物质、危险特性和名录代码，不能只按名称判断。",
          "14", "危险废物识别审核", "危废类别或代码缺失",
          ["固废产生环节", "危废代码", "危险特性", "处置去向"],
          [ref("国家危险废物名录", "危险废物代码", "危险废物类别和代码识别")]),
    entry("危险废物识别", "GB 18597-2023 危险废物贮存污染控制标准", "贮存设施",
          "危险废物暂存间应核对防渗、防雨、防流失、分区分类、标识和台账等贮存要求。",
          "14", "危险废物识别审核", "危废暂存间措施笼统",
          ["危废暂存间位置", "防渗措施", "标识", "台账制度"],
          [ref("GB 18597-2023", "贮存设施", "危险废物贮存污染控制要求")]),
    entry("危险废物识别", "HJ 2025-2012 危险废物收集贮存运输技术规范", "收集贮存运输",
          "危险废物收集、包装、转运和委外处置应核对分类收集、包装容器、转移联单和资质单位要求。",
          "14", "危险废物识别审核", "危废转移处置要求不完整",
          ["危废收集方式", "包装容器", "转移联单", "处置单位资质"],
          [ref("HJ 2025-2012", "收集贮存运输", "危险废物全过程管理要求")]),
    entry("危险废物识别", "GB 18599-2020 一般工业固体废物贮存和填埋污染控制标准", "一般固废",
          "一般工业固体废物贮存场所应与危险废物分开管理，并说明防渗漏、防雨淋、防扬尘等措施。",
          "14", "危险废物识别审核", "一般固废和危废管理混同",
          ["一般固废清单", "贮存场所", "防治措施"],
          [ref("GB 18599-2020", "一般工业固废贮存", "一般工业固体废物污染控制要求")]),

    # 15 VOC total control
    entry("VOCs总量控制", "广东省重点行业建设项目 VOCs 总量指标管理要求", "总量替代",
          "涉 VOCs 新、改、扩建项目应说明总量控制指标、替代来源、核算方法和削减量来源。",
          "15", "VOCs总量控制审核", "VOCs 总量控制只列排放量未列来源",
          ["VOCs 排放量", "总量指标来源说明", "替代削减方案"],
          [ref("广东省重点行业建设项目 VOCs 总量指标管理要求", "总量指标", "VOCs 总量替代与来源说明")]),
    entry("VOCs总量控制", "广东省工业源挥发性有机物减排量核算方法", "减排量核算",
          "VOCs 总量替代或减排量核算应说明基准排放、治理效率、削减措施和核算过程。",
          "15", "VOCs总量控制审核", "总量替代缺少计算过程",
          ["减排量核算表", "治理效率", "替代来源"],
          [ref("广东省工业源挥发性有机物减排量核算方法", "核算方法", "VOCs 减排量核算")]),
    entry("VOCs总量控制", "GB 37822-2019 / 地方 VOCs 管控要求", "源头替代",
          "总量控制审核应同步核对低 VOCs 原辅材料替代和无组织控制措施，不能只看末端排放量。",
          "15", "VOCs总量控制审核", "总量控制与源头替代脱节",
          ["原辅材料 VOCs 含量", "源头替代说明", "无组织控制措施"],
          [ref("GB 37822-2019", "VOCs 控制", "源头和无组织控制", OFFICIAL_SOURCES["GB 37822-2019"]["url"])]),
]


STANDARD_RE = re.compile(
    r"(GB(?:/T)?\s*[-/—]?\s*\d{3,5}(?:[-—]\d{2,4})?|HJ\s*[-/—]?\s*\d{2,4}(?:[-—]\d{2,4})?|DB44\s*/?\s*\d{2,4}(?:[-—]\d{2,4})?|环办环评〔?\d{4}〕?\d+号|佛环〔?\d{4}〕?\d+号|顺府发〔?\d{4}〕?\d+号|粤环[\u4e00-\u9fa5]*〔?\d{4}〕?\d+号)"
)


def normalize_ref(text):
    text = text.replace("—", "-").replace("－", "-").replace(" ", "")
    text = text.replace("GB/T", "GB/T ").replace("GB", "GB ").replace("HJ", "HJ ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_existing():
    items = []
    with INPUT_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def add_ids(existing, new_entries):
    max_id = 0
    for item in existing:
        m = re.match(r"STD_(\d+)", item.get("id", ""))
        if m:
            max_id = max(max_id, int(m.group(1)))
    out = []
    seen_requirements = {i.get("requirement", "").strip() for i in existing}
    for item in new_entries:
        if item["requirement"].strip() in seen_requirements:
            continue
        max_id += 1
        item = {"id": f"STD_{max_id:03d}", **item}
        out.append(item)
        seen_requirements.add(item["requirement"].strip())
    return out


def skill_from_ref(std):
    s = std.upper()
    if "4754" in s:
        return "01_国民经济行业类别审核"
    if "3095" in s or "3838" in s:
        return "05_环境质量现状数据审核"
    if "3096" in s or "12348" in s:
        return "06_环境质量执行标准审核"
    if any(x in s for x in ["31572", "37822", "14554", "16297", "DB44/27", "DB44 27", "2367", "DB44/26", "DB44 26"]):
        return "07_污染物排放标准审核"
    if "1122" in s:
        return "08_产污系数适用性审核"
    if "2026" in s:
        return "13_活性炭参数审核"
    if any(x in s for x in ["18597", "18599", "2025"]):
        return "14_危险废物识别审核"
    if "粤环" in std or "佛环" in std:
        return "15_VOCs总量控制审核"
    if "顺府" in std:
        return "03_三线一单符合性审核"
    return "manual_check_needed"


def scan_report_refs():
    sample_root = ROOT / "05_样本链（按项目组织）"
    counts = Counter()
    examples = {}
    by_file = defaultdict(set)
    for path in sample_root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in STANDARD_RE.findall(line):
                std = normalize_ref(match)
                counts[std] += 1
                by_file[path].add(std)
                if std not in examples:
                    rel = path.relative_to(ROOT).as_posix()
                    examples[std] = (rel, lineno, line[:220].replace("\t", " "))
    rows = []
    for std, count in counts.most_common():
        rel, lineno, snippet = examples[std]
        rows.append({
            "standard_ref": std,
            "count": count,
            "suggested_skill": skill_from_ref(std),
            "example_file": rel,
            "example_line": lineno,
            "example_snippet": snippet,
            "review_status": "manual_check_needed",
        })
    return rows


def write_jsonl(items):
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_md(existing, additions, report_rows):
    by_skill = defaultdict(list)
    for item in additions:
        by_skill[item.get("skill_name", "未分组")].append(item)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# 塑胶行业环评法规/标准依据库 V4（技能库对齐试点）\n\n")
        f.write("> 试点说明：本文件在 V3 深度版基础上扩展，不覆盖 V3。新增条目主要按 15 个审核 skill 对齐，并标记为 `manual_check_needed`，供人工复核后再决定是否并入正式库。\n\n")
        f.write(f"- V3 原有条目：{len(existing)} 条\n")
        f.write(f"- 本次新增试点条目：{len(additions)} 条\n")
        f.write(f"- V4 合计：{len(existing) + len(additions)} 条\n")
        f.write(f"- 从样本链报告中抽取的标准引用候选：{len(report_rows)} 类\n\n")
        f.write("## 新增条目按 skill 分布\n\n")
        f.write("| skill | 新增条目数 |\n| --- | ---: |\n")
        for skill, items in sorted(by_skill.items()):
            f.write(f"| {skill} | {len(items)} |\n")
        f.write("\n## 新增试点条目\n\n")
        for item in additions:
            f.write(f"### {item['id']} — {item['module']}\n\n")
            f.write(f"- skill: {item.get('skill_id', '')} {item.get('skill_name', '')}\n")
            f.write(f"- 来源: {item.get('source_file', '')}；章节/条款: {item.get('source_section', '')}\n")
            f.write(f"- 复核状态: {item.get('review_status', '')}\n")
            f.write(f"- 触发场景: {'；'.join(item.get('trigger', []))}\n")
            f.write(f"- 审核要求: {item.get('requirement', '')}\n")
            f.write(f"- 所需证据: {'；'.join(item.get('check_evidence', []))}\n")
            if item.get("notes"):
                f.write(f"- 备注: {item['notes']}\n")
            f.write("\n")
        f.write("## 样本链报告标准引用试点\n\n")
        f.write("详见 `standard_reference_pilot_from_reports.csv`。该表仅说明终稿/受理稿/修改意见中实际出现过哪些标准引用，不等于这些引用一定正确。\n")


def write_report_csv(rows):
    with OUT_REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "standard_ref",
                "count",
                "suggested_skill",
                "example_file",
                "example_line",
                "example_snippet",
                "review_status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_manifest():
    with OUT_MANIFEST.open("w", encoding="utf-8") as f:
        f.write("# V4 标准来源下载与解析说明\n\n")
        f.write("本文件记录本次扩展标准库时核对的公开来源。PDF/附件仅下载到本地 `_source_downloads_v4/` 供解析使用，不提交到 GitHub。\n\n")
        f.write("| 标准 | 名称 | 官方来源 | 本地处理 |\n| --- | --- | --- | --- |\n")
        for std, meta in OFFICIAL_SOURCES.items():
            f.write(f"| {std} | {meta['title']} | {meta['url']} | {meta['local_note']} |\n")
        f.write("\n## 使用边界\n\n")
        f.write("- 新增条目均为试点条目，默认需要人工复核。\n")
        f.write("- 对限值、表号、行业适用边界等内容，应以正式标准文本和专家复核结果为准。\n")
        f.write("- 报告中抽取的标准引用只能作为候选，不代表报告原引用一定正确。\n")


def main():
    existing = load_existing()
    additions = add_ids(existing, SKILL_ENTRIES)
    all_items = existing + additions
    report_rows = scan_report_refs()
    write_jsonl(all_items)
    write_md(existing, additions, report_rows)
    write_report_csv(report_rows)
    write_manifest()
    print(json.dumps({
        "existing": len(existing),
        "added": len(additions),
        "total": len(all_items),
        "report_reference_candidates": len(report_rows),
        "outputs": [
            str(OUT_JSONL.relative_to(ROOT)),
            str(OUT_MD.relative_to(ROOT)),
            str(OUT_REPORT_CSV.relative_to(ROOT)),
            str(OUT_MANIFEST.relative_to(ROOT)),
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
