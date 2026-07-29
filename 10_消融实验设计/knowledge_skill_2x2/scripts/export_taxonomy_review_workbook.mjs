import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const taskRoot = process.cwd();
const csvPath =
  process.argv[2] ?? path.resolve(taskRoot, "taxonomy/question_taxonomy_210.csv");
const outputPath =
  process.argv[3] ?? path.resolve(taskRoot, "taxonomy/taxonomy_review_workbook.xlsx");
const previewDir = path.resolve(taskRoot, "reports");

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "题目分类" });
const data = workbook.worksheets.getItem("题目分类");
const definitions = workbook.worksheets.add("分类定义");
const statistics = workbook.worksheets.add("分类统计");

data.showGridLines = false;
data.freezePanes.freezeRows(1);
data.freezePanes.freezeColumns(2);
data.getRange("A1:T211").format.font = { name: "Microsoft YaHei", size: 10 };
data.getRange("A1:T1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF", name: "Microsoft YaHei", size: 10 },
  wrapText: true,
  verticalAlignment: "center",
};
data.getRange("A1:T211").format.borders = {
  insideHorizontal: { style: "thin", color: "#E2E8F0" },
  bottom: { style: "thin", color: "#CBD5E1" },
};
data.getRange("A2:T211").format.verticalAlignment = "top";
data.getRange("A2:T211").format.rowHeight = 30;
data.getRange("A:A").format.columnWidth = 28;
data.getRange("B:B").format.columnWidth = 12;
data.getRange("C:F").format.columnWidth = 25;
data.getRange("G:G").format.columnWidth = 34;
data.getRange("H:J").format.columnWidth = 20;
data.getRange("K:N").format.columnWidth = 20;
data.getRange("O:T").format.columnWidth = 24;
data.getRange("G2:G211").format.wrapText = true;
data.getRange("L2:L211").format.wrapText = true;
data.getRange("Q2:T211").format.wrapText = true;

data.getRange("C2:C211").dataValidation = {
  rule: {
    type: "list",
    values: [
      "industry_classification",
      "environmental_investment",
      "environmental_quality_data",
      "water_emission_standard",
      "air_emission_standard",
      "noise_emission_standard",
      "solid_waste_standard",
    ],
  },
};
data.getRange("D2:D211").dataValidation = {
  rule: { type: "list", values: ["L1_understanding", "L2_application", "L3_analysis"] },
};
data.getRange("E2:E211").dataValidation = {
  rule: {
    type: "list",
    values: [
      "factual_extraction",
      "quantitative_verification",
      "rule_applicability",
      "consistency_comparison",
      "multi_evidence_synthesis",
    ],
  },
};
data.getRange("F2:F211").dataValidation = {
  rule: {
    type: "list",
    values: [
      "report_grounding",
      "basis_grounding",
      "numerical_accuracy",
      "procedural_reasoning",
      "evidence_integration",
    ],
  },
};
for (const column of ["H", "I"]) {
  data.getRange(`${column}2:${column}211`).dataValidation = {
    rule: { type: "list", values: ["low", "medium", "high"] },
  };
}
data.getRange("J2:J211").dataValidation = {
  rule: {
    type: "list",
    values: ["single_field", "single_section", "cross_section", "report_plus_external"],
  },
};
data.getRange("M2:M211").dataValidation = {
  rule: { type: "list", values: ["auto_default", "reviewed", "manual_override"] },
};
data.getRange("S2:S211").conditionalFormats.add("cellIs", {
  operator: "equal",
  formula: "TRUE",
  format: { fill: "#FDE9D9", font: { color: "#9C0006", bold: true } },
});
data.tables.add("A1:T211", true, "QuestionTaxonomyTable").style = "TableStyleMedium2";

const definitionRows = [
  ["分类维度", "枚举", "定义"],
  ["认知层级", "L1_understanding", "提取单一事实、字段、编号或基本概念"],
  ["认知层级", "L2_application", "应用公式、标准或规则，核对2—3项证据"],
  ["认知层级", "L3_analysis", "跨章节或内外部来源综合判断"],
  ["推理类型", "factual_extraction", "单一事实提取"],
  ["推理类型", "quantitative_verification", "比例、合计、单位、限值或公式复算"],
  ["推理类型", "rule_applicability", "按地区、行业、工艺、版本及时效匹配依据"],
  ["推理类型", "consistency_comparison", "报告内部或报告与外部资料比较"],
  ["推理类型", "multi_evidence_synthesis", "多证据综合形成结论"],
  ["功能能力", "report_grounding", "准确提取和使用报告证据"],
  ["功能能力", "basis_grounding", "选择真实、现行且适用的依据"],
  ["功能能力", "numerical_accuracy", "公式、数值和单位准确"],
  ["功能能力", "procedural_reasoning", "多步骤审核顺序和升级处理"],
  ["功能能力", "evidence_integration", "跨章节、跨来源证据整合"],
  ["证据跨度", "single_field", "单一字段"],
  ["证据跨度", "single_section", "单一章节"],
  ["证据跨度", "cross_section", "跨章节"],
  ["证据跨度", "report_plus_external", "报告加外部依据"],
];
definitions.getRange(`A1:C${definitionRows.length}`).values = definitionRows;
definitions.showGridLines = false;
definitions.freezePanes.freezeRows(1);
definitions.getRange("A1:C1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF", name: "Microsoft YaHei" },
};
definitions.getRange(`A2:C${definitionRows.length}`).format = {
  font: { name: "Microsoft YaHei", size: 10 },
  wrapText: true,
  verticalAlignment: "top",
};
definitions.getRange("A:A").format.columnWidth = 16;
definitions.getRange("B:B").format.columnWidth = 34;
definitions.getRange("C:C").format.columnWidth = 58;
definitions.tables.add(`A1:C${definitionRows.length}`, true, "TaxonomyDefinitionsTable").style =
  "TableStyleMedium2";

const dimensions = [
  ["审核领域", "C", [
    "industry_classification",
    "environmental_investment",
    "environmental_quality_data",
    "water_emission_standard",
    "air_emission_standard",
    "noise_emission_standard",
    "solid_waste_standard",
  ]],
  ["认知层级", "D", ["L1_understanding", "L2_application", "L3_analysis"]],
  ["推理类型", "E", [
    "factual_extraction",
    "quantitative_verification",
    "rule_applicability",
    "consistency_comparison",
    "multi_evidence_synthesis",
  ]],
  ["主要功能能力", "F", [
    "report_grounding",
    "basis_grounding",
    "numerical_accuracy",
    "procedural_reasoning",
    "evidence_integration",
  ]],
];
statistics.showGridLines = false;
statistics.getRange("A1:C1").values = [["维度", "标签", "题数"]];
statistics.getRange("A1:C1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF", name: "Microsoft YaHei" },
};
let rowIndex = 2;
for (const [dimension, column, labels] of dimensions) {
  for (const label of labels) {
    statistics.getRange(`A${rowIndex}:B${rowIndex}`).values = [[dimension, label]];
    statistics.getRange(`C${rowIndex}`).formulas = [
      [`=COUNTIF('题目分类'!$${column}$2:$${column}$211,B${rowIndex})`],
    ];
    rowIndex += 1;
  }
}
statistics.getRange(`A2:C${rowIndex - 1}`).format = {
  font: { name: "Microsoft YaHei", size: 10 },
};
statistics.getRange("A:A").format.columnWidth = 20;
statistics.getRange("B:B").format.columnWidth = 36;
statistics.getRange("C:C").format.columnWidth = 12;
statistics.tables.add(`A1:C${rowIndex - 1}`, true, "TaxonomyStatisticsTable").style =
  "TableStyleMedium2";

const checks = await workbook.inspect({
  kind: "table",
  sheetId: "分类统计",
  range: `A1:C${rowIndex - 1}`,
  include: "values,formulas",
  maxChars: 6000,
  tableMaxRows: 30,
  tableMaxCols: 4,
});
console.log(checks.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  maxChars: 3000,
});
console.log(errors.ndjson);

await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, filename] of [
  ["题目分类", "A1:T28", "taxonomy_review_data.preview.png"],
  ["分类定义", `A1:C${definitionRows.length}`, "taxonomy_review_definitions.preview.png"],
  ["分类统计", `A1:C${rowIndex - 1}`, "taxonomy_review_statistics.preview.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(
    path.join(previewDir, filename),
    new Uint8Array(await preview.arrayBuffer()),
  );
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, rows: 210, sheets: 3 }));
