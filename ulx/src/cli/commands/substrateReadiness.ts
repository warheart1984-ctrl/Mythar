import { existsSync, readFileSync } from "fs";
import { resolve } from "path";

interface SubstrateReadinessArgs {
  report: string;
}

function parseArgs(argv: string[]): SubstrateReadinessArgs {
  const args: SubstrateReadinessArgs = {
    report: ".ulx-migration/substrate-readiness.json"
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--report") {
      args.report = argv[++index] || args.report;
    }
  }

  return args;
}

export function substrateReadiness(argv: string[]): number {
  const args = parseArgs(argv);
  const reportPath = resolve(args.report);
  if (!existsSync(reportPath)) {
    console.error(`Substrate readiness report not found: ${reportPath}`);
    return 1;
  }

  try {
    const payload = JSON.parse(readFileSync(reportPath, "utf8")) as unknown;
    console.log(JSON.stringify(payload, null, 2));
    return 0;
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    return 1;
  }
}
