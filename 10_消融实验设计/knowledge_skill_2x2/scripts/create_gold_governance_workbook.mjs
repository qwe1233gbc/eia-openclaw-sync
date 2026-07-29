import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.cwd(), "10_消融实验设计/knowledge_skill_2x2");
const inputs = JSON.parse(await fs.readFile(path.join(root, ".cache/workbook_inputs.json"), "utf8"));
const outputPath = path.join(root, "gold_governance/环评审核问答_金标治理工作簿_v1.xlsx");
const previewDir = path.join(root, "gold_governance/reports/workbook_previews");

const originalFields = [
  "date", "canonical_project_id", "version_round", "report_name", "project_name",
  "question_id", "audit_module", "question", "answer", "evidence", "source_basis",
  "scarcity_check", "verifiability_check", "manual_check", "人工判断", "人工备注",
  "润色后答案", "修改类型", "是否需要人工复核", "AI标注备注", "来源文件", "审核类别",
];
const governanceFields = [
  "raw_manual_judgement", "normalized_judgement_candidate", "normalized_judgement_final",
  "gold_review_status", "evidence_sufficiency", "item_quality_status",
  "basis_verification_status", "taxonomy_review_status", "experiment_inclusion",
  "review_queue_type", "reviewer_1", "reviewer_1_date", "reviewer_2", "reviewer_2_date",
  "adjudicator", "adjudication_note", "gold_version", "source_row_number",
  "auto_mapping_rule", "auto_flag_reason", "human_review_note",
];
const taxonomyFields = [
  "audit_domain", "cognitive_level", "reasoning_type", "primary_functional_capability",
  "secondary_capabilities", "knowledge_dependency", "workflow_dependency", "evidence_span",
  "template_default_used", "taxonomy_source_override_reason", "classification_status",
  "taxonomy_version", "taxonomy_override_reason",
];
const fields = [...originalFields, ...governanceFields, ...taxonomyFields];
const colLetter = (n) => {
  let s = "";
  for (; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + ((n - 1) % 26)) + s;
  return s;
};
const fieldCol = Object.fromEntries(fields.map((x, i) => [x, colLetter(i + 1)]));

const workbook = await Workbook.fromCSV(
  "项目,说明\n金标治理工作簿,候选映射与人工复核工作台；不代表金标已完成\n重要约束,normalized_judgement_final 仅人工填写；任何脚本不得自动设置已冻结\n当前状态,210题均未复核、未冻结；未运行A/B/C/D实验或GPT评分\n复核顺序,30道异常题→18题趋势候选→A类→正式候选→其余候选池\n冻结门槛,先运行 scripts/validate_gold_freeze.py",
  { sheetName: "00_使用说明" },
);

const headerFormat = {
  font: { bold: true, color: "#FFFFFF", name: "Microsoft YaHei", size: 10 },
  wrapText: true,
  verticalAlignment: "center",
};
const originalHeader = { ...headerFormat, fill: "#1F4E78" };
const governanceHeader = { ...headerFormat, fill: "#C65911" };
const taxonomyHeader = { ...headerFormat, fill: "#548235" };
const editable = [
  "normalized_judgement_final", "gold_review_status", "evidence_sufficiency",
  "item_quality_status", "basis_verification_status", "taxonomy_review_status",
  "experiment_inclusion", "review_queue_type", "reviewer_1", "reviewer_1_date",
  "reviewer_2", "reviewer_2_date", "adjudicator", "adjudication_note", "gold_version",
  "human_review_note", "taxonomy_override_reason",
];

function normalizeCell(v) {
  if (v === null || v === undefined || v === "") return null;
  if (typeof v === "object") return JSON.stringify(v);
  return v;
}

function addDataSheet(name, rows, tableName) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  const matrix = [fields, ...rows.map((r) => fields.map((f) => normalizeCell(r[f])))];
  const endRow = matrix.length;
  const endCol = colLetter(fields.length);
  sheet.getRange(`A1:${endCol}${endRow}`).values = matrix;
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(6);
  sheet.getRange(`A1:V1`).format = originalHeader;
  sheet.getRange(`W1:AQ1`).format = governanceHeader;
  sheet.getRange(`AR1:${endCol}1`).format = taxonomyHeader;
  sheet.getRange(`A2:${endCol}${endRow}`).format = {
    font: { name: "Microsoft YaHei", size: 9 },
    verticalAlignment: "top",
    wrapText: true,
  };
  sheet.getRange(`A1:${endCol}${endRow}`).format.borders = {
    insideHorizontal: { style: "thin", color: "#E2E8F0" },
    insideVertical: { style: "thin", color: "#EDF2F7" },
    bottom: { style: "thin", color: "#CBD5E1" },
  };
  sheet.getRange(`A2:${endCol}${endRow}`).format.rowHeight = 36;
  sheet.getRange("A:C").format.columnWidth = 13;
  sheet.getRange("D:G").format.columnWidth = 23;
  sheet.getRange("H:K").format.columnWidth = 42;
  sheet.getRange("L:V").format.columnWidth = 20;
  sheet.getRange("W:BD").format.columnWidth = 22;
  for (const f of editable) {
    const c = fieldCol[f];
    sheet.getRange(`${c}2:${c}${endRow}`).format.fill = "#FFF2CC";
  }
  if (endRow > 1) {
    sheet.tables.add(`A1:${endCol}${endRow}`, true, tableName).style = "TableStyleMedium2";
    sheet.getRange(`${fieldCol.auto_flag_reason}2:${fieldCol.auto_flag_reason}${endRow}`).conditionalFormats.add("custom", {
      formula: `=LEN(${fieldCol.auto_flag_reason}2)>0`,
      format: { fill: "#F4CCCC", font: { color: "#9C0006" } },
    });
    sheet.getRange(`${fieldCol.evidence_sufficiency}2:${fieldCol.evidence_sufficiency}${endRow}`).conditionalFormats.add("cellIs", {
      operator: "equal", formula: '"不足"', format: { fill: "#FFD966", font: { color: "#7F6000" } },
    });
    sheet.getRange(`${fieldCol.gold_review_status}2:${fieldCol.gold_review_status}${endRow}`).conditionalFormats.add("cellIs", {
      operator: "equal", formula: '"已冻结"', format: { fill: "#C6E0B4", font: { color: "#006100", bold: true } },
    });
    const lists = {
      normalized_judgement_final: ["无误", "存在错误", "存在缺漏", "证据不足", "需人工复核", "待判断"],
      gold_review_status: ["未复核", "一审完成", "二审完成", "已裁决", "已冻结", "排除"],
      evidence_sufficiency: ["充分", "部分充分", "不足", "原始材料缺失", "待判断"],
      item_quality_status: ["有效", "表述歧义", "字段错位", "题答不匹配", "重复", "原始材料缺失", "排除", "待判断"],
      basis_verification_status: ["已核验", "部分核验", "未核验", "不需要外部依据", "待判断"],
      taxonomy_review_status: ["自动默认", "人工确认", "人工覆盖"],
      experiment_inclusion: ["候选池", "趋势实验候选", "趋势实验冻结", "正式实验候选", "正式实验冻结", "排除"],
      review_queue_type: ["A_仅待终审", "B_证据不足", "C_题目或材料问题", "D_无需复核候选", "待分流"],
    };
    for (const [f, values] of Object.entries(lists)) {
      const c = fieldCol[f];
      sheet.getRange(`${c}2:${c}${endRow}`).dataValidation = { rule: { type: "list", values } };
    }
  }
  return sheet;
}

const use = workbook.worksheets.getItem("00_使用说明");
use.showGridLines = false;
use.getRange("A1:B6").format = { font: { name: "Microsoft YaHei", size: 11 }, wrapText: true, verticalAlignment: "top" };
use.getRange("A1:B1").format = originalHeader;
use.getRange("A:A").format.columnWidth = 22;
use.getRange("B:B").format.columnWidth = 90;
use.getRange("A2:B6").format.rowHeight = 38;

addDataSheet("01_全部210题", inputs.records, "All210Table");
addDataSheet("02_30道异常题", inputs.anomalies, "Anomaly30Table");
addDataSheet("03_A类仅待终审", inputs.A, "QueueATable");
addDataSheet("04_B类证据不足", inputs.B, "QueueBTable");
addDataSheet("05_C类题目材料问题", inputs.C, "QueueCTable");
addDataSheet("06_D类无需复核候选", inputs.D, "QueueDTable");
addDataSheet("07_18题趋势候选", inputs.pilot, "Pilot18Table");
addDataSheet("08_正式实验候选", inputs.formal, "FormalCandidateTable");

const mapping = workbook.worksheets.add("09_标签映射规则");
const mappingRows = [
  ["原始人工判断", "候选映射", "处理原则"],
  ["正确", "无误", "仅写候选字段"],
  ["无误", "无误", "仅写候选字段"],
  ["存在错误", "存在错误", "仅写候选字段"],
  ["存在缺漏", "存在缺漏", "仅写候选字段"],
  ["需复核", "需人工复核", "等待人工复核"],
  ["不正确", "待判断", "人工区分错误或缺漏"],
  ["需修正", "待判断", "人工区分实质问题或表达优化"],
  ["无法判断", "待判断", "人工区分证据/材料/未审核"],
  ["空白", "待判断", "不得自动补填"],
  ["112", "待判断", "字段错位"],
  ["长说明", "抽取候选结论", "保留原文且必须人工确认"],
];
mapping.getRange(`A1:C${mappingRows.length}`).values = mappingRows;
mapping.getRange("A1:C1").format = governanceHeader;
mapping.getRange(`A2:C${mappingRows.length}`).format = { font: { name: "Microsoft YaHei" }, wrapText: true };
mapping.getRange("A:C").format.columnWidth = 35;
mapping.tables.add(`A1:C${mappingRows.length}`, true, "MappingRulesTable").style = "TableStyleMedium2";

const defs = workbook.worksheets.add("10_四维分类定义");
const defRows = [
  ["维度", "枚举/说明"],
  ["审核领域", "industry_classification / environmental_investment / environmental_quality_data / water_emission_standard / air_emission_standard / noise_emission_standard / solid_waste_standard"],
  ["认知层级", "L1_understanding / L2_application / L3_analysis"],
  ["推理类型", "factual_extraction / quantitative_verification / rule_applicability / consistency_comparison / multi_evidence_synthesis"],
  ["主要功能能力", "report_grounding / basis_grounding / numerical_accuracy / procedural_reasoning / evidence_integration"],
  ["知识依赖度", "low / medium / high"],
  ["Workflow依赖度", "low / medium / high"],
  ["证据跨度", "single_field / single_section / cross_section / report_plus_external"],
  ["覆盖规则", "18题与正式候选实验前逐题人工确认；人工覆盖必须填写 taxonomy_override_reason；不得为平衡分布篡改分类。"],
];
defs.getRange(`A1:B${defRows.length}`).values = defRows;
defs.getRange("A1:B1").format = taxonomyHeader;
defs.getRange(`A2:B${defRows.length}`).format = { font: { name: "Microsoft YaHei" }, wrapText: true };
defs.getRange("A:A").format.columnWidth = 24;
defs.getRange("B:B").format.columnWidth = 100;
defs.tables.add(`A1:B${defRows.length}`, true, "TaxonomyDefinitionsTable").style = "TableStyleMedium4";

const dash = workbook.worksheets.add("11_统计看板");
dash.getRange("A1:C1").values = [["指标", "数量", "说明"]];
dash.getRange("A1:C1").format = originalHeader;
const stats = [
  ["总题数", `=COUNTA('01_全部210题'!$F$2:$F$211)`, "应为210"],
  ["人工终值已填", `=COUNTIF('01_全部210题'!$Y$2:$Y$211,\"<>\")`, "脚本生成时应为0"],
  ["已冻结", `=COUNTIF('01_全部210题'!$Z$2:$Z$211,\"已冻结\")`, "脚本生成时应为0"],
  ["异常题", `=COUNTIF('01_全部210题'!$AB$2:$AB$211,\"<>有效\")`, "候选质量非有效"],
  ["A类", `=COUNTIF('01_全部210题'!$AF$2:$AF$211,\"A_仅待终审\")`, "候选分流"],
  ["B类", `=COUNTIF('01_全部210题'!$AF$2:$AF$211,\"B_证据不足\")`, "候选分流"],
  ["C类", `=COUNTIF('01_全部210题'!$AF$2:$AF$211,\"C_题目或材料问题\")`, "候选分流"],
  ["D类", `=COUNTIF('01_全部210题'!$AF$2:$AF$211,\"D_无需复核候选\")`, "需有终审证据"],
  ["分类自动默认", `=COUNTIF('01_全部210题'!$AD$2:$AD$211,\"自动默认\")`, "实验前需逐题确认"],
];
stats.forEach((r, i) => {
  const row = i + 2;
  dash.getRange(`A${row}`).values = [[r[0]]];
  dash.getRange(`B${row}`).formulas = [[r[1]]];
  dash.getRange(`C${row}`).values = [[r[2]]];
});
dash.getRange("A:C").format.columnWidth = 30;
dash.getRange("A2:C10").format = { font: { name: "Microsoft YaHei", size: 11 }, rowHeight: 28 };
dash.tables.add("A1:C10", true, "DashboardTable").style = "TableStyleMedium2";

const changes = workbook.worksheets.add("12_变更日志");
changes.getRange("A1:D4").values = [
  ["日期", "版本", "变更", "责任"],
  ["2026-07-29", "v1", "建立候选映射、异常识别、复核分流与实验候选池", "Codex自动处理（候选）"],
  ["2026-07-29", "v1", "纠正旧版18题 sample_selection_frozen=true 为未冻结候选", "Codex自动处理"],
  ["待填写", "待填写", "人工终值、证据、依据、分类、审核及冻结记录", "人工审核者"],
];
changes.getRange("A1:D1").format = governanceHeader;
changes.getRange("A2:D4").format = { font: { name: "Microsoft YaHei" }, wrapText: true };
changes.getRange("A:D").format.columnWidth = 35;
changes.getRange("A4:D4").format.fill = "#FFF2CC";
changes.tables.add("A1:D4", true, "ChangeLogTable").style = "TableStyleMedium9";

const errorCheck = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  maxChars: 4000,
});
console.log(errorCheck.ndjson);
const dashboardCheck = await workbook.inspect({
  kind: "table", sheetId: "11_统计看板", range: "A1:C10",
  include: "values,formulas", maxChars: 4000, tableMaxRows: 12, tableMaxCols: 4,
});
console.log(dashboardCheck.ndjson);

await fs.mkdir(previewDir, { recursive: true });
const previews = [
  ["00_使用说明", "A1:B6"], ["01_全部210题", "A1:AF14"], ["02_30道异常题", "A1:AF14"],
  ["03_A类仅待终审", "A1:AF14"], ["04_B类证据不足", "A1:AF14"], ["05_C类题目材料问题", "A1:AF14"],
  ["06_D类无需复核候选", "A1:AF4"], ["07_18题趋势候选", "A1:AF14"], ["08_正式实验候选", "A1:AF14"],
  ["09_标签映射规则", "A1:C12"], ["10_四维分类定义", "A1:B9"], ["11_统计看板", "A1:C10"], ["12_变更日志", "A1:D4"],
];
for (const [sheetName, range] of previews) {
  const png = await workbook.render({ sheetName, range, scale: 0.8, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName}.png`), new Uint8Array(await png.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, sheets: previews.length, rows: inputs.records.length }));
