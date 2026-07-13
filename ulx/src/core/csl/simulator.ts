import type { CslReplayRecord, CslRuntimeIntent, CslRuntimePolicy } from "../../types/csl.js";
import { RuntimeEngine } from "./runtime.js";

export interface SimulationResult {
  policy_version: string;
  decisions: Array<{
    intent_id: string;
    decision_id: string;
    outcome: string;
  }>;
}

export interface SimulationComparison {
  intent_id: string;
  outcomes: Record<string, string>;
  changed: boolean;
}

export class GovernanceSimulator {
  constructor(private readonly runtime: RuntimeEngine) {}

  simulate(intentStream: CslRuntimeIntent[], policyVersions: CslRuntimePolicy[]): Record<string, SimulationResult> {
    const results: Record<string, SimulationResult> = {};
    for (const policy of policyVersions) {
      const decisions = intentStream.map((intent) => {
        const agent = this.runtime.listAgents().find((entry) => entry.id === intent.agent_id);
        if (!agent) {
          throw new Error(`Agent not found for intent ${intent.id}`);
        }
        const constraints = this.runtime.deriveConstraints(policy, intent);
        const decision = this.runtime.resolveDecision(intent, agent, policy, constraints);
        this.runtime.ciems.replay.verifyDecision(policy.version, intent, decision);
        return {
          intent_id: intent.id,
          decision_id: decision.id,
          outcome: decision.outcome
        };
      });
      results[policy.version] = {
        policy_version: policy.version,
        decisions
      };
    }
    return results;
  }

  compare(results: Record<string, SimulationResult>): SimulationComparison[] {
    const normalized = Object.fromEntries(
      Object.entries(results).map(([policyVersion, result]) => [
        policyVersion,
        result.decisions.map((decision) => ({
          intent_id: decision.intent_id,
          outcome: decision.outcome
        }))
      ])
    );
    return this.runtime.ciems.replay.comparePolicyVersions(normalized);
  }

  replayEvents(): CslReplayRecord[] {
    return this.runtime.ciems.replay.getEvents();
  }
}
