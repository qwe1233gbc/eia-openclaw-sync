import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const taskRoot = process.cwd();
const projectRoot = path.resolve(taskRoot, "../../..");
const inputPath =
  process.argv[2] ??
  path.join(projectRoot, "05_QA测试集", "四大类问答对_最终版.xlsx");
const outputPath =
  process.argv[3] ??
  path.resolve(taskRoot, ".cache/source_questions.json");

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("全部问答对");
const used = sheet.getUsedRange(true);
const matrix = sheet.getRange(used.address).values;
const headers = matrix[0];
const records = matrix.slice(1).map((row) =>
  Object.fromEntries(headers.map((header, index) => [header, row[index] ?? null])),
);
const payload = {
  source_workbook: inputPath,
  sheet: sheet.name,
  used_range: used.address,
  extracted_at: new Date().toISOString(),
  headers,
  records,
};
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, JSON.stringify(payload, null, 2), "utf8");
console.log(JSON.stringify({ outputPath, records: records.length, usedRange: used.address }));
