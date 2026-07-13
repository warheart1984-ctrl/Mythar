import { readFileSync } from "fs";
import { createMigrationEngine } from "../../core/migration/engine.js";

interface MigrationCliArgs {
  root: string;
  command: "census" | "replay" | "rewind" | "restore" | "verify" | "plan";
  substrateId?: string;
  snapshotId?: string;
  runtimeJson?: string;
}

function parseArgs(argv: string[]): MigrationCliArgs {
  const args: MigrationCliArgs = {
    root: "ulx/.ulx-migration",
    command: "census"
  };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--root") {
      args.root = argv[++index] || args.root;
      continue;
    }
    if (value === "--substrate-id") {
      args.substrateId = argv[++index] || undefined;
      continue;
    }
    if (value === "--snapshot-id") {
      args.snapshotId = argv[++index] || undefined;
      continue;
    }
    if (value === "--runtime-json") {
      args.runtimeJson = argv[++index] || undefined;
      continue;
    }
    if (value === "census" || value === "replay" || value === "rewind" || value === "restore" || value === "verify" || value === "plan") {
      args.command = value;
    }
  }
  return args;
}

export function migrationCommand(argv: string[]): number {
  const args = parseArgs(argv);
  const engine = createMigrationEngine({ root: args.root });

  if (args.command === "census") {
    console.log(JSON.stringify(engine.census(), null, 2));
    return 0;
  }

  if (args.command === "replay") {
    console.log(JSON.stringify(engine.replay(args.substrateId), null, 2));
    return 0;
  }

  if (args.command === "rewind") {
    console.log(JSON.stringify(engine.rewind(args.substrateId), null, 2));
    return 0;
  }

  if (args.command === "restore") {
    if (!args.snapshotId) {
      console.error("missing --snapshot-id");
      return 1;
    }
    console.log(JSON.stringify(engine.restore(args.snapshotId), null, 2));
    return 0;
  }

  if (args.command === "verify") {
    if (!args.runtimeJson) {
      console.error("missing --runtime-json");
      return 1;
    }
    const runtime = JSON.parse(readFileSync(args.runtimeJson, "utf8")) as {
      substrateId: string;
      id: string;
      phase?: string;
      status?: "draft" | "active" | "restored";
      evidence?: Array<{ id: string; kind: string; path?: string; summary?: string }>;
      lineage?: string[];
      replayable?: boolean;
      updatedAt?: string;
    };
    console.log(JSON.stringify(engine.verify(engine.canonicalize(runtime)), null, 2));
    return 0;
  }

  if (!args.runtimeJson) {
    console.error("missing --runtime-json");
    return 1;
  }
  const runtime = JSON.parse(readFileSync(args.runtimeJson, "utf8")) as {
    substrateId: string;
    name?: string;
    phase?: "census" | "planned" | "applied" | "verified" | "rewound" | "restored";
    status?: "draft" | "active" | "restored";
    evidence?: Array<{ id: string; kind: string; path?: string; summary?: string }>;
    lineage?: string[];
    replayable?: boolean;
    restorePointId?: string;
    updatedAt?: string;
  };
  console.log(JSON.stringify(engine.plan(engine.canonicalize(runtime)), null, 2));
  return 0;
}
