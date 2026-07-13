import { existsSync } from "fs";
import { spawnSync } from "node:child_process";
import { resolve } from "path";

interface MergeSubstrateArgs {
  manifest: string;
  targetRepo: string;
  workspace: string;
  dryRun: boolean;
  planOnly: boolean;
  output: string;
}

function parseArgs(argv: string[]): MergeSubstrateArgs {
  const args: MergeSubstrateArgs = {
    manifest: "",
    targetRepo: "",
    workspace: "",
    dryRun: false,
    planOnly: false,
    output: ""
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--manifest") {
      args.manifest = argv[++index] || "";
      continue;
    }
    if (value === "--target-repo") {
      args.targetRepo = argv[++index] || "";
      continue;
    }
    if (value === "--workspace") {
      args.workspace = argv[++index] || "";
      continue;
    }
    if (value === "--output") {
      args.output = argv[++index] || "";
      continue;
    }
    if (value === "--dry-run") {
      args.dryRun = true;
      continue;
    }
    if (value === "--plan-only") {
      args.planOnly = true;
      continue;
    }
  }

  return args;
}

function pythonCommandCandidates(): string[] {
  if (process.platform === "win32") {
    return ["python", "py", "python3"];
  }
  return ["python3", "python", "py"];
}

function runPythonMigrator(command: string, scriptPath: string, args: string[]): { ok: boolean; stdout: string; stderr: string; code: number } {
  const result = spawnSync(command, [scriptPath, ...args], {
    cwd: process.cwd(),
    encoding: "utf8",
    shell: false
  });

  return {
    ok: result.status === 0,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    code: typeof result.status === "number" ? result.status : 1
  };
}

export function mergeSubstrates(argv: string[]): number {
  const args = parseArgs(argv);
  if (!args.manifest || !args.targetRepo) {
    console.error("Usage: merge-substrates --manifest <manifest_json> --target-repo <repo> [--workspace <dir>] [--dry-run] [--plan-only] [--output <path>]");
    return 1;
  }

  const scriptPath = resolve("src/core/tools/migrations/ulx_normalize_substrates.py");
  if (!existsSync(scriptPath)) {
    console.error(`Migration script not found: ${scriptPath}`);
    return 1;
  }

  const normalizedArgs = [
    "--manifest",
    resolve(args.manifest),
    "--target-repo",
    resolve(args.targetRepo)
  ];
  if (args.workspace) {
    normalizedArgs.push("--workspace", resolve(args.workspace));
  }
  if (args.dryRun) {
    normalizedArgs.push("--dry-run");
  }
  if (args.planOnly) {
    normalizedArgs.push("--plan-only");
  }
  if (args.output) {
    normalizedArgs.push("--output", resolve(args.output));
  }

  const commands = pythonCommandCandidates();
  let lastResult: { ok: boolean; stdout: string; stderr: string; code: number } | null = null;
  for (const command of commands) {
    const result = runPythonMigrator(command, scriptPath, normalizedArgs);
    lastResult = result;
    if (result.code !== 127 && result.code !== 9009) {
      if (result.ok) {
        if (result.stdout.trim()) {
          console.log(result.stdout.trimEnd());
        }
        if (result.stderr.trim()) {
          console.error(result.stderr.trimEnd());
        }
        return 0;
      }
      if (result.code !== 1 || result.stderr || result.stdout) {
        if (result.stdout.trim()) {
          console.log(result.stdout.trimEnd());
        }
        if (result.stderr.trim()) {
          console.error(result.stderr.trimEnd());
        }
        return result.code;
      }
    }
  }

  const fallback = lastResult;
  if (fallback?.stdout.trim()) {
    console.log(fallback.stdout.trimEnd());
  }
  if (fallback?.stderr.trim()) {
    console.error(fallback.stderr.trimEnd());
  }
  console.error("No usable Python executable found for substrate merge.");
  return 1;
}
