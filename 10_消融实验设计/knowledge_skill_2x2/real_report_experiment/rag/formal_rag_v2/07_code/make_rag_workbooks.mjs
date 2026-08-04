import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const ROOT = String.raw`D:\华南理工项目\智慧环评\skill\ABCD实验工作区\04_RAG资料补齐与验证`;
const PREVIEW = path.join(ROOT, "08_reports", "xlsx_previews");
await fs.mkdir(PREVIEW, { recursive: true });

const COLORS = {
  navy: "#17365D",
  blue: "#1F4E78",
  sky: "#D9EAF7",
  light: "#F4F7FA",
  grid: "#D9E1F2",
  green: "#E2F0D9",
  yellow: "#FFF2CC",
  red: "#FCE4D6",
  gray: "#E7E6E6",
  white: "#FFFFFF",
  text: "#1F2937",
};

function colLetter(n) {
  let s = "";
  while (n > 0) {
    n--;
    s = String.fromCharCode(65 + (n % 26)) + s;
    n = Math.floor(n / 26);
  }
  return s;
}

function statusFill(value) {
  if (["complete", "complete_primary_source"].includes(value)) return COLORS.green;
  if (["complete_with_warning", "version_uncertain", "primary_source_not_indexed"].includes(value)) return COLORS.yellow;
  if (["incomplete", "missing", "derived_only"].includes(value)) return COLORS.red;
  if (["not_required"].includes(value)) return COLORS.gray;
  return COLORS.white;
}

function addReadme(wb, title, purpose, caveats) {
  const ws = wb.worksheets.add("README");
  ws.showGridLines = false;
  ws.mergeCells("A1:H2");
  ws.getRange("A1:H2").values = [[title]];
  ws.getRange("A1:H2").format = {
    fill: COLORS.navy,
    font: { color: COLORS.white, bold: true, size: 18 },
    verticalAlignment: "center",
    horizontalAlignment: "left",
  };
  ws.getRange("A4:B9").values = [
    ["生成日期", "2026-08-04"],
    ["用途", purpose],
    ["数据范围", "21道黄色测试问答"],
    ["生成原则", "正式来源优先；历史适用与现行参考分列；冻结前不读取金标"],
    ["关键限制", caveats],
    ["状态色", "绿色=完整；黄色=完整但需警告；红色=缺失/不完整；灰色=不需要外部RAG"],
  ];
  ws.getRange("A4:A9").format = { fill: COLORS.sky, font: { bold: true, color: COLORS.navy } };
  ws.getRange("A4:B9").format.borders = { preset: "all", style: "thin", color: COLORS.grid };
  ws.getRange("A4:B9").format.wrapText = true;
  ws.getRange("A:A").format.columnWidth = 18;
  ws.getRange("B:B").format.columnWidth = 85;
  ws.freezePanes.freezeRows(2);
  return ws;
}

function addDataSheet(wb, sheetName, rows, statusField) {
  const ws = wb.worksheets.add(sheetName);
  ws.showGridLines = false;
  const headers = Object.keys(rows[0] ?? { message: "无数据" });
  const matrix = [headers, ...rows.map((r) => headers.map((h) => {
    const v = r[h];
    if (Array.isArray(v)) return v.join(";");
    if (v === null || v === undefined) return "";
    return v;
  }))];
  const end = colLetter(headers.length);
  ws.getRange(`A1:${end}${matrix.length}`).values = matrix;
  ws.getRange(`A1:${end}1`).format = {
    fill: COLORS.blue,
    font: { color: COLORS.white, bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.grid },
  };
  ws.getRange(`A2:${end}${matrix.length}`).format = {
    font: { color: COLORS.text, size: 10 },
    verticalAlignment: "top",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.grid },
  };
  for (let r = 2; r <= matrix.length; r++) {
    if (r % 2 === 0) ws.getRange(`A${r}:${end}${r}`).format.fill = COLORS.light;
  }
  const statusIndex = headers.indexOf(statusField);
  if (statusIndex >= 0) {
    const c = colLetter(statusIndex + 1);
    for (let r = 2; r <= matrix.length; r++) {
      ws.getRange(`${c}${r}`).format.fill = statusFill(String(matrix[r - 1][statusIndex]));
      ws.getRange(`${c}${r}`).format.font = { bold: true, color: COLORS.text };
    }
  }
  for (let i = 0; i < headers.length; i++) {
    const h = headers[i];
    const c = colLetter(i + 1);
    let width = 16;
    if (/question|title|notes|action|clause|data|applicability|source_ids|source_path|official_url|knowledge/i.test(h)) width = 34;
    if (/question$|notes$|coverage_note|manual_note|source_basis/i.test(h)) width = 48;
    if (/sha256/i.test(h)) width = 24;
    ws.getRange(`${c}:${c}`).format.columnWidth = width;
  }
  ws.getRange(`1:1`).format.rowHeight = 42;
  ws.freezePanes.freezeRows(1);
  ws.freezePanes.freezeColumns(2);
  return { ws, headers, rowCount: rows.length };
}

function addStatusSummary(wb, dataSheet, statusCol, statuses, dataRows) {
  const ws = wb.worksheets.add("Status Summary");
  ws.showGridLines = false;
  ws.mergeCells("A1:D2");
  ws.getRange("A1:D2").values = [["状态汇总"]];
  ws.getRange("A1:D2").format = { fill: COLORS.navy, font: { color: COLORS.white, bold: true, size: 16 }, verticalAlignment: "center" };
  ws.getRange("A4:B4").values = [["状态", "数量（公式）"]];
  ws.getRange("A4:B4").format = { fill: COLORS.blue, font: { color: COLORS.white, bold: true }, borders: { preset: "all", style: "thin", color: COLORS.grid } };
  const rows = statuses.map((s) => [s, null]);
  ws.getRange(`A5:B${4 + rows.length}`).values = rows;
  for (let i = 0; i < statuses.length; i++) {
    const r = 5 + i;
    ws.getRange(`B${r}`).formulas = [[`=COUNTIF('${dataSheet}'!${statusCol}2:${statusCol}${dataRows + 1},A${r})`]];
    ws.getRange(`A${r}`).format.fill = statusFill(statuses[i]);
  }
  const totalRow = 5 + statuses.length;
  ws.getRange(`A${totalRow}:B${totalRow}`).values = [["合计", null]];
  ws.getRange(`B${totalRow}`).formulas = [[`=SUM(B5:B${totalRow - 1})`]];
  ws.getRange(`A5:B${totalRow}`).format.borders = { preset: "all", style: "thin", color: COLORS.grid };
  ws.getRange(`A${totalRow}:B${totalRow}`).format = { fill: COLORS.sky, font: { bold: true, color: COLORS.navy }, borders: { preset: "all", style: "thin", color: COLORS.grid } };
  ws.getRange("A:A").format.columnWidth = 30;
  ws.getRange("B:B").format.columnWidth = 18;
  ws.freezePanes.freezeRows(2);
  return ws;
}

async function renderAll(wb, prefix, sheetNames) {
  const inspect = await wb.inspect({ kind: "sheet", include: "id,name", maxChars: 4000 });
  await fs.writeFile(path.join(PREVIEW, `${prefix}_inspect.txt`), inspect.ndjson ?? String(inspect), "utf8");
  for (const name of sheetNames) {
    const png = await wb.render({ sheetName: name, autoCrop: "all", scale: 0.9, format: "png" });
    await fs.writeFile(path.join(PREVIEW, `${prefix}_${name.replaceAll(" ", "_")}.png`), new Uint8Array(await png.arrayBuffer()));
  }
}

async function exportWorkbook(wb, outPath) {
  const file = await SpreadsheetFile.exportXlsx(wb);
  await file.save(outPath);
}

const matrixRows = JSON.parse(await fs.readFile(path.join(ROOT, "00_gap_audit", "qa_rag_requirement_matrix.workbook_data.json"), "utf8"));
{
  const wb = Workbook.create();
  const sheetNames = ["README", "Requirement Matrix", "Status Summary"];
  addReadme(wb, "21题RAG知识需求矩阵", "逐题反推正式RAG所需外部依据、现有来源状态与补充动作", "2022顺德公报与GB/T 18920-2020全文缺失时不得标记完整");
  const { headers, rowCount } = addDataSheet(wb, "Requirement Matrix", matrixRows, "current_status");
  const statusCol = colLetter(headers.indexOf("current_status") + 1);
  addStatusSummary(wb, "Requirement Matrix", statusCol, ["complete_primary_source", "primary_source_not_indexed", "derived_only", "version_uncertain", "missing", "not_required"], rowCount);
  await exportWorkbook(wb, path.join(ROOT, "00_gap_audit", "qa_rag_requirement_matrix.xlsx"));
  await renderAll(wb, "requirement_matrix", sheetNames);
}

const versionRows = JSON.parse(await fs.readFile(path.join(ROOT, "01_source_governance", "version_and_applicability_report.workbook_data.json"), "utf8"));
{
  const wb = Workbook.create();
  const sheetNames = ["README", "Source Registry", "Version Risks", "Status Summary"];
  addReadme(wb, "正式来源版本与适用性报告", "登记来源、版本、地区、历史适用和2026现行参考", "新版本不得机械倒用于旧报告；缺全文来源保持manual_source_upload_required");
  const { headers, rowCount } = addDataSheet(wb, "Source Registry", versionRows, "validity_status");
  const riskRows = versionRows.filter((r) => r.manual_source_upload_required || !["现行", ""].includes(String(r.validity_status)) || r.historical_applicability || r.current_reference);
  addDataSheet(wb, "Version Risks", riskRows, "validity_status");
  const statusCol = colLetter(headers.indexOf("validity_status") + 1);
  const statuses = [...new Set(versionRows.map((r) => String(r.validity_status)))];
  addStatusSummary(wb, "Source Registry", statusCol, statuses, rowCount);
  await exportWorkbook(wb, path.join(ROOT, "01_source_governance", "version_and_applicability_report.xlsx"));
  await renderAll(wb, "version_report", sheetNames);
}

const coverageRows = JSON.parse(await fs.readFile(path.join(ROOT, "05_rag_evaluation", "qa_source_coverage_review.workbook_data.json"), "utf8"));
{
  const wb = Workbook.create();
  const sheetNames = ["README", "Coverage Review", "Status Summary"];
  addReadme(wb, "21题冻结后RAG覆盖率复核", "在RAG快照冻结后读取金标字段，仅用于评价必要来源是否命中", "金标字段不得进入查询、分块、排序或冻结上下文");
  const { headers, rowCount } = addDataSheet(wb, "Coverage Review", coverageRows, "coverage_conclusion");
  const statusCol = colLetter(headers.indexOf("coverage_conclusion") + 1);
  addStatusSummary(wb, "Coverage Review", statusCol, ["complete", "complete_with_warning", "incomplete", "not_required"], rowCount);
  await exportWorkbook(wb, path.join(ROOT, "05_rag_evaluation", "qa_source_coverage_review.xlsx"));
  await renderAll(wb, "coverage_review", sheetNames);
}

console.log(JSON.stringify({ ok: true, previewDir: PREVIEW }, null, 2));
