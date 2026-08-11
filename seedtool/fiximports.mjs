import { readFileSync, writeFileSync, existsSync, globSync } from "node:fs";
import { dirname, resolve as resolvePath } from "node:path";

const files = globSync("Blueprint/src/modules/**/*.ts");

function resolveTarget(fromFile, spec) {
  if (!spec.startsWith(".")) return null;
  const base = resolvePath(dirname(fromFile), spec);
  for (const cand of [base, base + ".ts", base + ".tsx", base + "/index.ts"]) {
    if (existsSync(cand) && cand.endsWith(".ts")) return cand;
  }
  return null;
}

const valueCache = new Map();
function valueExports(file) {
  if (valueCache.has(file)) return valueCache.get(file);
  const set = new Set();
  const src = readFileSync(file, "utf8");
  const decl =
    /^export\s+(?:declare\s+)?(?:abstract\s+)?(?:class|const|let|var|function|async function|enum)\s+(\w+)/gm;
  for (const m of src.matchAll(decl)) set.add(m[1]);
  // re-exports: export { A, B } from './x'  /  export { A }
  for (const m of src.matchAll(/^export\s*\{([^}]*)\}/gm)) {
    for (const part of m[1].split(",")) {
      const name = part.trim().split(/\s+as\s+/).pop();
      if (name && !part.trim().startsWith("type ")) set.add(name.trim());
    }
  }
  valueCache.set(file, set);
  return set;
}

let changed = 0;
for (const f of files) {
  const src = readFileSync(f, "utf8");
  let out = src.replace(
    /^import\s*\{([^}]*)\}\s*from\s*(['"])([^'"]+)\2\s*;?/gm,
    (full, names, q, spec) => {
      const target = resolveTarget(f, spec);
      if (!target) return full;
      const vals = valueExports(target);
      const valueSide = [];
      const typeSide = [];
      for (const raw of names.split(",")) {
        const part = raw.trim();
        if (!part) continue;
        if (part.startsWith("type ")) {
          typeSide.push(part.slice(5).trim());
          continue;
        }
        const orig = part.split(/\s+as\s+/)[0].trim();
        (vals.has(orig) ? valueSide : typeSide).push(part);
      }
      if (typeSide.length === 0) return full;
      const lines = [];
      if (valueSide.length)
        lines.push(`import {${valueSide.join(", ")}} from ${q}${spec}${q};`);
      lines.push(`import type {${typeSide.join(", ")}} from ${q}${spec}${q};`);
      return lines.join("\n");
    }
  );
  if (out !== src) {
    writeFileSync(f, out);
    changed++;
  }
}
console.log("patched", changed, "files");
