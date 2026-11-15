export const columns = ["id","created_at","backend","size","qubits","median_seconds","gflops","fidelity"];
export function serializeHistory(history, format) {
  if (format === "json") return JSON.stringify(history, null, 2);
  if (format !== "csv") throw new Error("Unsupported export format");
  const quote = value => '"' + String(value ?? "").replaceAll('"', '""') + '"';
  const rows = history.map(x => ({...x.payload.result,id:x.id,created_at:x.created_at}));
  return [columns.join(","), ...rows.map(row => columns.map(k => quote(row[k])).join(","))].join("\r\n");
}
