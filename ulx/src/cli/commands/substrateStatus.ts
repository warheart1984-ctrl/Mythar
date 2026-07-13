import { readJson } from "../../core/fs.js";

export function substrateStatus(substrateId: string): number {
  const substrate = readJson<Record<string, unknown>>(`substrates/${substrateId}/substrate.json`);
  console.log(JSON.stringify(substrate, null, 2));
  return 0;
}
