import { existsSync, readdirSync, readFileSync } from "fs";
import { join } from "path";

export interface MigrationCensusEntry {
  substrateId: string;
  substratePath: string;
  status: string;
  workspace?: string;
}

export interface MigrationCensusResult {
  root: string;
  entries: MigrationCensusEntry[];
}

function substrateStatus(path: string): string {
  try {
    const raw = readFileSync(path, "utf8");
    const parsed = JSON.parse(raw) as { status?: string };
    return parsed.status ?? "unknown";
  } catch {
    return "unknown";
  }
}

export function censusSubstrates(root = "substrates"): MigrationCensusResult {
  if (!existsSync(root)) {
    return { root, entries: [] };
  }
  const entries = readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const substratePath = join(root, entry.name, "substrate.json");
      return {
        substrateId: entry.name,
        substratePath,
        status: existsSync(substratePath) ? substrateStatus(substratePath) : "missing"
      };
    })
    .sort((left, right) => left.substrateId.localeCompare(right.substrateId));
  return { root, entries };
}
