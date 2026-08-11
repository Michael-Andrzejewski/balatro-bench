import { analyzeSeed } from "./Blueprint/src/modules/ImmolateWrapper/index.ts";
import { options } from "./Blueprint/src/modules/const.ts";

for (const v of ["10014", "10103", "10106"]) {
  const res: any = analyzeSeed(
    { seed: "BENCHMRK", deck: "Red Deck", stake: "White Stake", gameVersion: v, antes: 3, cardsPerAnte: 8 },
    { buys: {}, sells: {}, showCardSpoilers: true, unlocks: options, events: [], updates: [], maxMiscCardSource: 10, lockedCards: {}, customDeck: [] }
  );
  console.log(`--- version ${v} ---`);
  for (let n = 1; n <= 3; n++) {
    const a = res.antes[String(n)];
    console.log(`  A${n} voucher=${a.voucher} boss=${a.boss} tags=${a.tags.join("/")}`);
    console.log(`  A${n} packs: ${JSON.stringify(a.packQueue.slice(0, 6))}`);
    console.log(`  A${n} shop0-5: ${a.queue.slice(0, 6).map((c: any) => c.name).join(", ")}`);
  }
}
