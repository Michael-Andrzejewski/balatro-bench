import { readFileSync } from "node:fs";
const d = JSON.parse(readFileSync("seed.json", "utf8")).antes;
for (let n = 1; n <= 12; n++) {
  const a = d[String(n)];
  if (!a) continue;
  console.log(`--- ANTE ${n} ---`);
  console.log("  voucherQueue:", JSON.stringify(a.voucherQueue));
  console.log("  tagsQueue:", JSON.stringify(a.tagsQueue));
  console.log("  bossQueue:", JSON.stringify(a.bossQueue?.slice?.(0, 4) ?? a.bossQueue));
  console.log("  packQueue:", JSON.stringify(a.packQueue?.slice(0, 10)));
}
