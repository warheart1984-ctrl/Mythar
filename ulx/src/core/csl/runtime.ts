import type {
  CslArtifactRecord,
  CslLineageEdge,
  CslRuntimeAgent,
  CslRuntimeConstraint,
  CslRuntimeDecision,
  CslRuntimeIntent,
  CslRuntimePolicy
} from "../../types/csl.js";
import { CIEMSIntegration } from "./integration.js";

export interface RuntimeRunResult {
  agent: CslRuntimeAgent;
  intent: CslRuntimeIntent;
  policy: CslRuntimePolicy;
  constraints: CslRuntimeConstraint[];
  decision: CslRuntimeDecision;
  artifacts: CslArtifactRecord[];
  lineage: CslLineageEdge[];
}

export interface RuntimeOptions {
  agents?: CslRuntimeAgent[];
  policies?: CslRuntimePolicy[];
}

function currentTimestamp(): string {
  return new Date().toISOString();
}

function stableJoin(parts: string[]): string {
  return parts.join("|");
}

function hashedId(prefix: string, parts: string[]): string {
  const seed = stableJoin(parts);
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) >>> 0;
  }
  return `${prefix}-${hash.toString(16).padStart(8, "0")}`;
}

function matchesRule(rule: string, intent: CslRuntimeIntent): boolean {
  if (rule === "*" || rule === "allow:*" || rule === "block:*" || rule === "escalate:*") {
    return true;
  }
  const [prefix, value] = rule.split(":", 2);
  if (!prefix || !value) {
    return false;
  }
  if (prefix === "kind") {
    return value === intent.kind;
  }
  if (prefix === "context") {
    return Object.values(intent.context).some((entry) => String(entry) === value);
  }
  return value === intent.kind;
}

function ruleSeverity(rule: string): "low" | "medium" | "high" {
  if (rule.startsWith("block:")) {
    return "high";
  }
  if (rule.startsWith("escalate:")) {
    return "medium";
  }
  return "low";
}

export class RuntimeEngine {
  private readonly agents: CslRuntimeAgent[];
  private readonly policies: CslRuntimePolicy[];
  private intentSequence = 0;
  private constraintSequence = 0;
  private decisionSequence = 0;

  constructor(public readonly ciems: CIEMSIntegration, options: RuntimeOptions = {}) {
    this.agents = [...(options.agents ?? [])];
    this.policies = [...(options.policies ?? [])];
  }

  registerAgent(agent: CslRuntimeAgent): CslRuntimeAgent {
    this.agents.push(agent);
    return agent;
  }

  registerPolicy(policy: CslRuntimePolicy): CslRuntimePolicy {
    this.policies.push(policy);
    return policy;
  }

  listAgents(): CslRuntimeAgent[] {
    return [...this.agents];
  }

  listPolicies(): CslRuntimePolicy[] {
    return [...this.policies];
  }

  generateIntent(agentId: string, kind: string, context: Record<string, unknown> = {}): CslRuntimeIntent {
    const agent = this.requireAgent(agentId);
    const sequence = this.intentSequence;
    this.intentSequence += 1;
    return {
      id: hashedId("intent", [agent.id, kind, String(sequence), stableJoin(Object.keys(context).sort())]),
      agent_id: agent.id,
      kind,
      context: { ...context },
      timestamp: currentTimestamp()
    };
  }

  selectPolicy(intent: CslRuntimeIntent): CslRuntimePolicy {
    const sorted = [...this.policies].sort((left, right) => {
      const tierCompare = (left.tier ?? 0) - (right.tier ?? 0);
      if (tierCompare !== 0) {
        return tierCompare;
      }
      const versionCompare = left.version.localeCompare(right.version);
      if (versionCompare !== 0) {
        return versionCompare;
      }
      return left.id.localeCompare(right.id);
    });
    const matching = sorted.find((policy) =>
      policy.enabled &&
      policy.rules.some((rule) => matchesRule(rule, intent))
    );
    const selected = matching ?? sorted.find((policy) => policy.enabled) ?? sorted[0];
    if (!selected) {
      throw new Error("No runtime policy available");
    }
    return selected;
  }

  deriveConstraints(policy: CslRuntimePolicy, intent: CslRuntimeIntent): CslRuntimeConstraint[] {
    return policy.rules.map((rule, index) => ({
      id: hashedId("constraint", [policy.id, intent.id, rule, String(index), String(this.constraintSequence + index)]),
      policy_id: policy.id,
      intent_id: intent.id,
      rule,
      severity: ruleSeverity(rule),
      timestamp: currentTimestamp()
    }));
  }

  resolveDecision(
    intent: CslRuntimeIntent,
    agent: CslRuntimeAgent,
    policy: CslRuntimePolicy,
    constraints: CslRuntimeConstraint[]
  ): CslRuntimeDecision {
    const sequence = this.decisionSequence;
    this.decisionSequence += 1;
    const blocked = constraints.some((constraint) => constraint.rule.startsWith("block:") && matchesRule(constraint.rule, intent));
    const escalated = !blocked && constraints.some((constraint) => constraint.rule.startsWith("escalate:") && matchesRule(constraint.rule, intent));
    const accepted = !blocked && !escalated && constraints.some((constraint) => constraint.rule.startsWith("allow:") && matchesRule(constraint.rule, intent));
    const outcome: CslRuntimeDecision["outcome"] = blocked ? "blocked" : escalated ? "escalated" : accepted ? "accepted" : "blocked";
    const reason = blocked
      ? "policy_blocked"
      : escalated
        ? "policy_escalated"
        : accepted
          ? "policy_accepted"
          : "no_matching_allow_rule";
    return {
      id: hashedId("decision", [intent.id, agent.id, policy.id, outcome, String(sequence)]),
      intent_id: intent.id,
      agent_id: agent.id,
      policy_id: policy.id,
      constraint_ids: constraints.map((constraint) => constraint.id),
      outcome,
      evidence: {
        agent_role: agent.role,
        policy_version: policy.version,
        rule_count: policy.rules.length
      },
      timestamp: currentTimestamp(),
      reason
    };
  }

  runOnce(agentId: string, kind: string, context: Record<string, unknown> = {}): RuntimeRunResult {
    const agent = this.requireAgent(agentId);
    const intent = this.generateIntent(agent.id, kind, context);
    const policy = this.selectPolicy(intent);
    const constraints = this.deriveConstraints(policy, intent);
    this.constraintSequence += constraints.length;
    const decision = this.resolveDecision(intent, agent, policy, constraints);

    const artifacts = [
      this.ciems.save_artifact(this.ciems.adapter.agent(agent)),
      this.ciems.save_artifact(this.ciems.adapter.intent(intent)),
      this.ciems.save_artifact(this.ciems.adapter.policy(policy)),
      ...constraints.map((constraint) => this.ciems.save_artifact(this.ciems.adapter.constraint(constraint))),
      this.ciems.save_artifact(this.ciems.adapter.decision(decision))
    ];

    const lineage: CslLineageEdge[] = [
      this.ciems.record_lineage({
        lineage_id: hashedId("lineage", [agent.id, intent.id, "generates"]),
        from: agent.id,
        to: intent.id,
        relation: "generates",
        artifact_id: artifacts[0].artifact_id,
        created_at: currentTimestamp(),
        evidence: { kind: intent.kind }
      }),
      this.ciems.record_lineage({
        lineage_id: hashedId("lineage", [policy.id, intent.id, "governedBy"]),
        from: policy.id,
        to: intent.id,
        relation: "governedBy",
        artifact_id: artifacts[2].artifact_id,
        policy_version: policy.version,
        created_at: currentTimestamp(),
        evidence: { rules: [...policy.rules] }
      }),
      ...constraints.map((constraint) =>
        this.ciems.record_lineage({
          lineage_id: hashedId("lineage", [constraint.policy_id, constraint.intent_id, constraint.id]),
          from: constraint.policy_id,
          to: constraint.id,
          relation: "generates",
          artifact_id: artifacts[3].artifact_id,
          policy_version: policy.version,
          intent_id: intent.id,
          created_at: currentTimestamp(),
          evidence: { rule: constraint.rule, severity: constraint.severity }
        })
      ),
      this.ciems.record_lineage({
        lineage_id: hashedId("lineage", [decision.id, intent.id, "resolves"]),
        from: decision.id,
        to: intent.id,
        relation: "resolves",
        artifact_id: artifacts[artifacts.length - 1].artifact_id,
        policy_version: policy.version,
        intent_id: intent.id,
        decision_id: decision.id,
        created_at: currentTimestamp(),
        evidence: { outcome: decision.outcome, reason: decision.reason }
      }),
      this.ciems.record_lineage({
        lineage_id: hashedId("lineage", [decision.id, policy.id, "governedBy"]),
        from: decision.id,
        to: policy.id,
        relation: "governedBy",
        artifact_id: artifacts[artifacts.length - 1].artifact_id,
        policy_version: policy.version,
        intent_id: intent.id,
        decision_id: decision.id,
        created_at: currentTimestamp(),
        evidence: { outcome: decision.outcome }
      })
    ];

    this.ciems.replay.verifyDecision(policy.version, intent, decision);

    return {
      agent,
      intent,
      policy,
      constraints,
      decision,
      artifacts,
      lineage
    };
  }

  runLoop(iterations: number, kind: string, context: Record<string, unknown> = {}): RuntimeRunResult[] {
    if (iterations <= 0) {
      return [];
    }
    const results: RuntimeRunResult[] = [];
    for (let index = 0; index < iterations; index += 1) {
      const agent = this.agents[index % this.agents.length];
      if (!agent) {
        throw new Error("No runtime agent available");
      }
      results.push(this.runOnce(agent.id, kind, { ...context, iteration: index }));
    }
    return results;
  }

  private requireAgent(agentId: string): CslRuntimeAgent {
    const agent = this.agents.find((entry) => entry.id === agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    return agent;
  }
}
