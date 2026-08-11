import { readFileSync } from "node:fs";

const d = JSON.parse(readFileSync("seed.json", "utf8")).antes;
const FROM = Number(process.env.FROM ?? 1);
const TO = Number(process.env.TO ?? 8);
const SHOP = Number(process.env.SHOP ?? 16);

const PACK_SIZE = {
  "Arcana Pack": [3, 1], "Jumbo Arcana Pack": [5, 1], "Mega Arcana Pack": [5, 2],
  "Celestial Pack": [3, 1], "Jumbo Celestial Pack": [5, 1], "Mega Celestial Pack": [5, 2],
  "Standard Pack": [3, 1], "Jumbo Standard Pack": [5, 1], "Mega Standard Pack": [5, 2],
  "Buffoon Pack": [2, 1], "Jumbo Buffoon Pack": [4, 1], "Mega Buffoon Pack": [4, 2],
  "Spectral Pack": [2, 1], "Jumbo Spectral Pack": [4, 1], "Mega Spectral Pack": [4, 2],
};
const SRC = {
  Arcana: "arcanaPack", Celestial: "celestialPack", Standard: "standardPack",
  Buffoon: "buffoonPack", Spectral: "spectralPack",
};

for (let n = FROM; n <= TO; n++) {
  const a = d[String(n)];
  if (!a) continue;
  console.log(`\n===== ANTE ${n} =====`);
  console.log(`BOSS: ${a.boss}   VOUCHER: ${a.voucher}   TAGS: ${a.tags.join(" / ")}`);

  const q = a.queue.slice(0, SHOP).map((c, i) => {
    const ed = c.edition && c.edition !== "No Edition" ? `[${c.edition}]` : "";
    const st = c.isEternal ? "(Eternal)" : c.isPerishable ? "(Perish)" : c.isRental ? "(Rental)" : "";
    return `${i}:${c.name}${ed}${st}`;
  });
  console.log("SHOP: " + q.join("  |  "));

  const cursor = {};
  const packs = a.packQueue.slice(0, 8).map((p) => {
    const kind = Object.keys(SRC).find((k) => p.includes(k));
    const src = Object.values(a.miscCardSources).find((s) => s.name === SRC[kind]);
    const [size] = PACK_SIZE[p] ?? [3, 1];
    const start = cursor[kind] ?? 0;
    cursor[kind] = start + size;
    const contents = (src?.cards ?? []).slice(start, start + size).map((c) => {
      const ed = c.edition && c.edition !== "No Edition" ? `[${c.edition}]` : "";
      const sl = c.seal && c.seal !== "No Seal" ? `{${c.seal}}` : "";
      const en = c.enhancements && c.enhancements !== "No Enhancement" ? `<${c.enhancements}>` : "";
      return `${c.name}${en}${ed}${sl}`;
    });
    return `${p} => ${contents.join(", ")}`;
  });
  console.log("PACKS:\n  " + packs.join("\n  "));
}
