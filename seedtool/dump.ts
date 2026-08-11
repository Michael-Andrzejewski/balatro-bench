import { analyzeSeed } from "./Blueprint/src/modules/ImmolateWrapper/index.ts";
import { options } from "./Blueprint/src/modules/const.ts";

const antes = Number(process.env.ANTES ?? 12);
const depth = Number(process.env.DEPTH ?? 25);

const res: any = analyzeSeed(
  {
    seed: "BENCHMRK",
    deck: "Red Deck",
    stake: "White Stake",
    gameVersion: "10106",
    antes,
    cardsPerAnte: depth,
  },
  {
    buys: {},
    sells: {},
    showCardSpoilers: true,
    unlocks: options,
    events: [],
    updates: [],
    maxMiscCardSource: Number(process.env.MISC ?? 40),
    lockedCards: {},
    customDeck: [],
  }
);

import { writeFileSync } from "node:fs";
writeFileSync("seed.json", JSON.stringify(res), "utf8");
console.log("wrote seed.json");
