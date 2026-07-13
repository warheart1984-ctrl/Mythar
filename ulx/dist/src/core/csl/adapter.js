function relationSet(relations) {
    return {
        generates: [...(relations.generates ?? [])],
        resolves: [...(relations.resolves ?? [])],
        governedBy: [...(relations.governedBy ?? [])],
        constrains: [...(relations.constrains ?? [])],
        promotesTo: [...(relations.promotesTo ?? [])],
        expandsTo: [...(relations.expandsTo ?? [])]
    };
}
function buildArtifact(artifactType, cslType, kind, tier, name, payload, relations, evolution, evidence, lineage, createdAt = new Date().toISOString()) {
    const id = String(payload.id ?? name);
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
export class DefaultCslAdapter {
    agent(agent) {
        return buildArtifact("Agent", "Struct", "Being", agent.tier ?? 0, agent.id, agent, { generates: ["Intent"], promotesTo: agent.promotes_to ? [agent.promotes_to] : [] }, { promotesTo: agent.promotes_to, expandsTo: [] }, { capabilities: [...agent.capabilities] }, [agent.id]);
    }
    policy(policy) {
        return buildArtifact("Policy", "Struct", "Cosmos", policy.tier ?? 0, policy.name, policy, { generates: ["Constraint"], promotesTo: policy.promotes_to ? [policy.promotes_to] : [], expandsTo: policy.expands_to ?? [] }, { promotesTo: policy.promotes_to, expandsTo: [...(policy.expands_to ?? [])] }, { rules: [...policy.rules], version: policy.version }, [policy.id, policy.version]);
    }
    intent(intent) {
        return buildArtifact("Intent", "Struct", "Cycle", 0, intent.kind, intent, { resolves: ["Decision"], governedBy: ["Policy"] }, { expandsTo: [] }, { context: { ...intent.context } }, [intent.agent_id, intent.id]);
    }
    constraint(constraint) {
        return buildArtifact("Constraint", "Struct", "Transcendence", 0, constraint.rule, constraint, { constrains: ["Decision"] }, { expandsTo: [] }, { severity: constraint.severity }, [constraint.policy_id, constraint.intent_id, constraint.id]);
    }
    decision(decision) {
        return buildArtifact("Decision", "Struct", "Cycle", 0, decision.reason, decision, { resolves: ["Intent"], governedBy: ["Policy"], constrains: ["Constraint"] }, { expandsTo: [] }, { outcome: decision.outcome, evidence: { ...decision.evidence } }, [decision.agent_id, decision.policy_id, decision.intent_id, decision.id]);
    }
}
