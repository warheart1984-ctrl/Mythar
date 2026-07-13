export class GovernanceSimulator {
    runtime;
    constructor(runtime) {
        this.runtime = runtime;
    }
    simulate(intentStream, policyVersions) {
        const results = {};
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
    compare(results) {
        const normalized = Object.fromEntries(Object.entries(results).map(([policyVersion, result]) => [
            policyVersion,
            result.decisions.map((decision) => ({
                intent_id: decision.intent_id,
                outcome: decision.outcome
            }))
        ]));
        return this.runtime.ciems.replay.comparePolicyVersions(normalized);
    }
    replayEvents() {
        return this.runtime.ciems.replay.getEvents();
    }
}
