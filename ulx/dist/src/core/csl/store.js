import { existsSync, readFileSync, mkdirSync, appendFileSync } from "fs";
import { dirname, join } from "path";
function ensureDirectory(path) {
    const dir = dirname(path);
    if (dir && !existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
    }
}
function readJsonl(path) {
    if (!existsSync(path)) {
        return [];
    }
    const raw = readFileSync(path, "utf8").trim();
    if (!raw) {
        return [];
    }
    return raw
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => JSON.parse(line));
}
function appendJsonl(path, data) {
    ensureDirectory(path);
    appendFileSync(path, `${JSON.stringify(data)}\n`, "utf8");
}
function stableStringify(value) {
    if (value === null || typeof value !== "object") {
        return JSON.stringify(value);
    }
    if (Array.isArray(value)) {
        return `[${value.map((entry) => stableStringify(entry)).join(",")}]`;
    }
    const entries = Object.entries(value).sort(([left], [right]) => left.localeCompare(right));
    return `{${entries.map(([key, entry]) => `${JSON.stringify(key)}:${stableStringify(entry)}`).join(",")}}`;
}
function artifactFile(root) {
    return join(root, "artifacts.jsonl");
}
function lineageFile(root) {
    return join(root, "lineage.jsonl");
}
function replayFile(root) {
    return join(root, "replay.jsonl");
}
export class FileCepArtifactStore {
    root;
    constructor(root = "constitutional/cep") {
        this.root = root;
    }
    saveArtifact(artifact) {
        appendJsonl(artifactFile(this.root), artifact);
        return artifact;
    }
    listArtifacts() {
        return readJsonl(artifactFile(this.root)).sort((left, right) => left.artifact_id.localeCompare(right.artifact_id));
    }
    getArtifact(artifactId) {
        return this.listArtifacts().find((artifact) => artifact.artifact_id === artifactId) ?? null;
    }
}
function nodeFromArtifact(artifact) {
    return {
        id: artifact.artifact_id,
        label: artifact.name,
        kind: artifact.kind,
        tier: artifact.tier
    };
}
function edgeFromLineage(edge) {
    return {
        from: edge.from,
        to: edge.to,
        type: edge.relation
    };
}
function uniqueNodesFromArtifacts(artifacts) {
    const nodes = new Map();
    for (const artifact of artifacts) {
        if (!nodes.has(artifact.artifact_id)) {
            nodes.set(artifact.artifact_id, nodeFromArtifact(artifact));
        }
    }
    return [...nodes.values()].sort((left, right) => left.id.localeCompare(right.id));
}
export class FileLineageStore {
    root;
    constructor(root = "constitutional/cep") {
        this.root = root;
    }
    record(edge) {
        appendJsonl(lineageFile(this.root), edge);
        return edge;
    }
    list() {
        return readJsonl(lineageFile(this.root)).sort((left, right) => {
            const createdCompare = left.created_at.localeCompare(right.created_at);
            if (createdCompare !== 0) {
                return createdCompare;
            }
            return left.lineage_id.localeCompare(right.lineage_id);
        });
    }
    findByArtifact(artifactId) {
        return this.list().filter((edge) => edge.artifact_id === artifactId ||
            edge.from === artifactId ||
            edge.to === artifactId ||
            edge.intent_id === artifactId ||
            edge.decision_id === artifactId);
    }
    buildEvolutionGraph(artifacts) {
        const edges = this.list()
            .filter((edge) => edge.relation === "promotesTo" || edge.relation === "expandsTo")
            .map(edgeFromLineage);
        return {
            nodes: uniqueNodesFromArtifacts(artifacts),
            edges
        };
    }
    buildGovernanceGraph(artifacts) {
        const edges = this.list()
            .filter((edge) => edge.relation !== "promotesTo" && edge.relation !== "expandsTo")
            .map(edgeFromLineage);
        return {
            nodes: uniqueNodesFromArtifacts(artifacts),
            edges
        };
    }
    getPromotionEvidence(promotionId, artifacts, replay) {
        const artifact = artifacts.find((entry) => entry.artifact_id === promotionId || entry.evolution.promotesTo === promotionId) ??
            null;
        const lineage = this.findByArtifact(promotionId);
        const replayMatches = replay.filter((entry) => entry.policy_version === promotionId || entry.decision_id === promotionId || entry.intent_id === promotionId);
        return {
            promotion_id: promotionId,
            artifact,
            lineage,
            replay: replayMatches
        };
    }
}
export class FileReplayStore {
    root;
    constructor(root = "constitutional/cep") {
        this.root = root;
    }
    verifyDecision(policyVersion, intent, decision) {
        const record = {
            replay_id: `replay-${createReplayId(policyVersion, intent.id, decision.id)}`,
            policy_version: policyVersion,
            intent_id: intent.id,
            decision_id: decision.id,
            approved: decision.outcome === "accepted",
            outcome: decision.outcome,
            notes: [intent.kind, decision.reason],
            timestamp: new Date().toISOString()
        };
        appendJsonl(replayFile(this.root), record);
        return record;
    }
    comparePolicyVersions(results) {
        const outcomesByIntent = new Map();
        const policies = Object.keys(results).sort((left, right) => left.localeCompare(right));
        for (const policyVersion of policies) {
            for (const decision of results[policyVersion] ?? []) {
                const outcomes = outcomesByIntent.get(decision.intent_id) ?? {};
                outcomes[policyVersion] = decision.outcome;
                outcomesByIntent.set(decision.intent_id, outcomes);
            }
        }
        return [...outcomesByIntent.entries()]
            .map(([intent_id, outcomes]) => ({
            intent_id,
            outcomes,
            changed: new Set(Object.values(outcomes)).size > 1
        }))
            .sort((left, right) => left.intent_id.localeCompare(right.intent_id));
    }
    getEvents() {
        return readJsonl(replayFile(this.root)).sort((left, right) => {
            const timestampCompare = left.timestamp.localeCompare(right.timestamp);
            if (timestampCompare !== 0) {
                return timestampCompare;
            }
            return left.replay_id.localeCompare(right.replay_id);
        });
    }
}
function createReplayId(policyVersion, intentId, decisionId) {
    return stableStringify({ policyVersion, intentId, decisionId }).replace(/[^a-zA-Z0-9]+/g, "-").slice(0, 32);
}
