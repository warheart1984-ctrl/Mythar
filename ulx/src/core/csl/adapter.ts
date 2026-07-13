import type {
  CslAdapter,
  CslArtifactRecord,
  CslCosmogenicKind,
  CslPrimitiveKind,
  CslRuntimeAgent,
  CslRuntimeConstraint,
  CslRuntimeDecision,
  CslRuntimeIntent,
  CslRuntimePolicy
} from "../../types/csl.js";

function relationSet(relations: Partial<CslArtifactRecord["relations"]>): CslArtifactRecord["relations"] {
  return {
    generates: [...(relations.generates ?? [])],
    resolves: [...(relations.resolves ?? [])],
    governedBy: [...(relations.governedBy ?? [])],
    constrains: [...(relations.constrains ?? [])],
    promotesTo: [...(relations.promotesTo ?? [])],
    expandsTo: [...(relations.expandsTo ?? [])]
  };
}

function buildArtifact<TPayload extends object>(
  artifactType: CslArtifactRecord["artifact_type"],
  cslType: CslPrimitiveKind,
  kind: CslCosmogenicKind,
  tier: number,
  name: string,
  payload: TPayload,
  relations: Partial<CslArtifactRecord["relations"]>,
  evolution: CslArtifactRecord["evolution"],
  evidence: Record<string, unknown>,
  lineage: string[],
  createdAt = new Date().toISOString()
): CslArtifactRecord<TPayload> {
  const id = String((payload as { id?: string }).id ?? name);
  return {
    artifact_id: `${artifactType}:${id}`,
    artifact_type: artifactType,
    cslType,
    kind,
    tier,
    name,
    payload,
    relations: relationSet(relations),
    evolution,
    evidence,
    lineage: [...lineage],
    created_at: createdAt
  };
}

export class DefaultCslAdapter implements CslAdapter {
  agent(agent: CslRuntimeAgent): CslArtifactRecord {
    return buildArtifact(
      "Agent",
      "Struct",
      "Being",
      agent.tier ?? 0,
      agent.id,
      agent,
      { generates: ["Intent"], promotesTo: agent.promotes_to ? [agent.promotes_to] : [] },
      { promotesTo: agent.promotes_to, expandsTo: [] },
      { capabilities: [...agent.capabilities] },
      [agent.id]
    );
  }

  policy(policy: CslRuntimePolicy): CslArtifactRecord {
    return buildArtifact(
      "Policy",
      "Struct",
      "Cosmos",
      policy.tier ?? 0,
      policy.name,
      policy,
      { generates: ["Constraint"], promotesTo: policy.promotes_to ? [policy.promotes_to] : [], expandsTo: policy.expands_to ?? [] },
      { promotesTo: policy.promotes_to, expandsTo: [...(policy.expands_to ?? [])] },
      { rules: [...policy.rules], version: policy.version },
      [policy.id, policy.version]
    );
  }

  intent(intent: CslRuntimeIntent): CslArtifactRecord {
    return buildArtifact(
      "Intent",
      "Struct",
      "Cycle",
      0,
      intent.kind,
      intent,
      { resolves: ["Decision"], governedBy: ["Policy"] },
      { expandsTo: [] },
      { context: { ...intent.context } },
      [intent.agent_id, intent.id]
    );
  }

  constraint(constraint: CslRuntimeConstraint): CslArtifactRecord {
    return buildArtifact(
      "Constraint",
      "Struct",
      "Transcendence",
      0,
      constraint.rule,
      constraint,
      { constrains: ["Decision"] },
      { expandsTo: [] },
      { severity: constraint.severity },
      [constraint.policy_id, constraint.intent_id, constraint.id]
    );
  }

  decision(decision: CslRuntimeDecision): CslArtifactRecord {
    return buildArtifact(
      "Decision",
      "Struct",
      "Cycle",
      0,
      decision.reason,
      decision,
      { resolves: ["Intent"], governedBy: ["Policy"], constrains: ["Constraint"] },
      { expandsTo: [] },
      { outcome: decision.outcome, evidence: { ...decision.evidence } },
      [decision.agent_id, decision.policy_id, decision.intent_id, decision.id]
    );
  }
}
