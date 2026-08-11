import { readFileSync } from "node:fs";
const d = JSON.parse(readFileSync("seed.json", "utf8")).antes;
const targets = (process.env.FIND ?? "Blueprint").split(",").map((s) => s.trim());

for (const n of Object.keys(d)) {
  const a = d[n];
  if (!a) continue;
  a.queue?.forEach((c, i) => {
    if (targets.includes(c.name))
      console.log(`ante ${n} SHOP slot ${i}: ${c.name} [${c.edition}] ${c.rarity ?? ""} ${c.isEternal ? "ETERNAL" : ""}${c.isPerishable ? "PERISH" : ""}${c.isRental ? "RENTAL" : ""}`);
  });
  const only = (process.env.SRC ?? "").split(",").filter(Boolean);
  for (const src of Object.values(a.miscCardSources ?? {})) {
    if (only.length && !only.includes(src.name)) continue;
    src.cards?.forEach((c, i) => {
      if (targets.includes(c.name))
        console.log(`ante ${n} ${src.name}[${i}]: ${c.name} [${c.edition ?? ""}]`);
    });
  }
}
