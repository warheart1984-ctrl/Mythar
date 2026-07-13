#!/usr/bin/env node
import { fileURLToPath } from "url";
import { chainValidate } from "./commands/chainValidate.js";
import { decisionLog } from "./commands/decisionLog.js";
import { launchReadiness } from "./commands/launchReadiness.js";
import { knowledgeIngest } from "./commands/knowledgeIngest.js";
import { mergeSubstrates } from "./commands/mergeSubstrates.js";
import { substrateReadiness } from "./commands/substrateReadiness.js";
import { sovereignOsConstitutionalKernel } from "./commands/sovereignOsConstitutionalKernel.js";
import { specificationDependencyGraph } from "./commands/specificationDependencyGraph.js";
import { specificationRegistry } from "./commands/specificationRegistry.js";
import { promote } from "./commands/promote.js";
import { substrateStatus } from "./commands/substrateStatus.js";
import { tui } from "./commands/tui.js";

const ROOT = fileURLToPath(new URL("../..", import.meta.url));
if (process.cwd() !== ROOT) {
  process.chdir(ROOT);
}

function usage(): void {
  console.log(
    [
      "ULX v0.1",
      "Commands:",
      "  chain-validate <substrate_id>",
      "  promote <substrate_id> <target_status>",
      "  knowledge-ingest <batch_json>",
      "  merge-substrates --manifest <manifest_json> --target-repo <repo> [--workspace <dir>] [--dry-run] [--plan-only] [--output <path>]",
      "  substrate-readiness [--report <report_json>]",
      "  launch-readiness",
      "  sovereign-os-constitutional-kernel",
      "  specification-dependency-graph",
      "  specification-registry",
      "  substrate-status <substrate_id>",
      "  decision-log <substrate_id>",
      "  tui <substrate_id>"
    ].join("\n")
  );
}

const [, , cmd, ...rest] = process.argv;

let exitCode = 1;
switch (cmd) {
  case "chain-validate":
    exitCode = chainValidate(rest[0] || "");
    break;
  case "promote":
    exitCode = promote(rest[0] || "", rest[1] || "");
    break;
  case "knowledge-ingest":
    exitCode = knowledgeIngest(rest[0] || "");
    break;
  case "merge-substrates":
    exitCode = mergeSubstrates(rest);
    break;
  case "substrate-readiness":
    exitCode = substrateReadiness(rest);
    break;
  case "launch-readiness":
  case "readiness":
    exitCode = launchReadiness();
    break;
  case "sovereign-os-constitutional-kernel":
  case "kernel-spec":
    exitCode = sovereignOsConstitutionalKernel();
    break;
  case "specification-dependency-graph":
  case "dependency-graph":
    exitCode = specificationDependencyGraph();
    break;
  case "specification-registry":
  case "registry":
    exitCode = specificationRegistry();
    break;
  case "substrate-status":
    exitCode = substrateStatus(rest[0] || "");
    break;
  case "decision-log":
    exitCode = decisionLog(rest[0] || "");
    break;
  case "tui":
    exitCode = tui(rest[0] || "sovereign-os");
    break;
  default:
    usage();
    break;
}

process.exitCode = exitCode;
