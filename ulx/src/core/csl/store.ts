import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync } from "fs";
import { dirname, join } from "path";
import type {
  CslArtifactRecord,
  CslEvidenceBundle,
  CslGraph,
  CslGraphEdge,
  CslGraphNode,
  CslLineageEdge,
  CslReplayRecord,
  CslRelationKind
} from "../../types/csl.js";

function ensureDirectory(path: string): void {
  const dir = dirname(path);
  if (dir && !existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function readJsonl<T>(path: string): T[] {
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
    .map((line) => JSON.parse(line) as T);
}

function appendJsonl(path: string, data: unknown): void {
  ensureDirectory(path);
  appendFileSync(path, `${JSON.stringify(data)}\n`, "utf8");
}

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((entry) => stableStringify(entry)).join(",")}]`;
  }
  const entries = Object.entries(value as Record<string, unknown>).sort(([left], [right]) =>
    left.localeCompare(right)
  );
  return `{${entries.map(([key, entry]) => `${JSON.stringify(key)}:${stableStringify(entry)}`).join(",")}}`;
}

function artifactFile(root: string): string {
  return join(root, "artifacts.jsonl");
}

function lineageFile(root: string): string {
  return join(root, "lineage.jsonl");
}

function replayFile(root: string): string {
  return join(root, "replay.jsonl");
}

export interface CepArtifactStore {
  saveArtifact<T extends CslArtifactRecord>(artifact: T): T;
  listArtifacts(): CslArtifactRecord[];
  getArtifact(artifactId: string): CslArtifactRecord | null;
}

export interface CiemsLineageStore {
  record(edge: CslLineageEdge): CslLineageEdge;
  list(): CslLineageEdge[];
  findByArtifact(artifactId: string): CslLineageEdge[];
  buildEvolutionGraph(artifacts: CslArtifactRecord[]): CslGraph;
  buildGovernanceGraph(artifacts: CslArtifactRecord[]): CslGraph;
  getPromotionEvidence(
    promotionId: string,
    artifacts: CslArtifactRecord[],
    replay: CslReplayRecord[]
  ): CslEvidenceBundle;
}

export interface CslReplayStore {
  verifyDecision(
    policyVersion: string,
    intent: { id: string; kind: string; agent_id: string },
    decision: { id: string; outcome: string; reason: string }
  ): CslReplayRecord;
  comparePolicyVersions(results: Record<string, Array<{ intent_id: string; outcome: string }>>): Array<{
    intent_id: string;
    outcomes: Record<string, string>;
    changed: boolean;
  }>;
  getEvents(): CslReplayRecord[];
}

export class FileCepArtifactStore implements CepArtifactStore {
  constructor(private readonly root = "constitutional/cep") {}

  saveArtifact<T extends CslArtifactRecord>(artifact: T): T {
    appendJsonl(artifactFile(this.root), artifact);
    return artifact;
  }

  listArtifacts(): CslArtifactRecord[] {
    return readJsonl<CslArtifactRecord>(artifactFile(this.root)).sort((left, right) =>
      left.artifact_id.localeCompare(right.artifact_id)
    );
  }

  getArtifact(artifactId: string): CslArtifactRecord | null {
    return this.listArtifacts().find((artifact) => artifact.artifact_id === artifactId) ?? null;
  }
}

function nodeFromArtifact(artifact: CslArtifactRecord): CslGraphNode {
  return {
    id: artifact.artifact_id,
    label: artifact.name,
    kind: artifact.kind,
    tier: artifact.tier
  };
}

function edgeFromLineage(edge: CslLineageEdge): CslGraphEdge {
  return {
    from: edge.from,
    to: edge.to,
    type: edge.relation
  };
}

function uniqueNodesFromArtifacts(artifacts: CslArtifactRecord[]): CslGraphNode[] {
  const nodes = new Map<string, CslGraphNode>();
  for (const artifact of artifacts) {
    if (!nodes.has(artifact.artifact_id)) {
      nodes.set(artifact.artifact_id, nodeFromArtifact(artifact));
    }
  }
  return [...nodes.values()].sort((left, right) => left.id.localeCompare(right.id));
}

export class FileLineageStore implements CiemsLineageStore {
  constructor(private readonly root = "constitutional/cep") {}

  record(edge: CslLineageEdge): CslLineageEdge {
    appendJsonl(lineageFile(this.root), edge);
    return edge;
  }

  list(): CslLineageEdge[] {
    return readJsonl<CslLineageEdge>(lineageFile(this.root)).sort((left, right) => {
      const createdCompare = left.created_at.localeCompare(right.created_at);
      if (createdCompare !== 0) {
        return createdCompare;
      }
      return left.lineage_id.localeCompare(right.lineage_id);
    });
  }

  findByArtifact(artifactId: string): CslLineageEdge[] {
    return this.list().filter(
      (edge) =>
        edge.artifact_id === artifactId ||
        edge.from === artifactId ||
        edge.to === artifactId ||
        edge.intent_id === artifactId ||
        edge.decision_id === artifactId
    );
  }

  buildEvolutionGraph(artifacts: CslArtifactRecord[]): CslGraph {
    const edges = this.list()
      .filter((edge) => edge.relation === "promotesTo" || edge.relation === "expandsTo")
      .map(edgeFromLineage);
    return {
      nodes: uniqueNodesFromArtifacts(artifacts),
      edges
    };
  }

  buildGovernanceGraph(artifacts: CslArtifactRecord[]): CslGraph {
    const edges = this.list()
      .filter((edge) => edge.relation !== "promotesTo" && edge.relation !== "expandsTo")
      .map(edgeFromLineage);
    return {
      nodes: uniqueNodesFromArtifacts(artifacts),
      edges
    };
  }

  getPromotionEvidence(
    promotionId: string,
    artifacts: CslArtifactRecord[],
    replay: CslReplayRecord[]
  ): CslEvidenceBundle {
    const artifact =
      artifacts.find((entry) => entry.artifact_id === promotionId || entry.evolution.promotesTo === promotionId) ??
      null;
    const lineage = this.findByArtifact(promotionId);
    const replayMatches = replay.filter(
      (entry) => entry.policy_version === promotionId || entry.decision_id === promotionId || entry.intent_id === promotionId
    );
    return {
      promotion_id: promotionId,
      artifact,
      lineage,
      replay: replayMatches
    };
  }
}

export class FileReplayStore implements CslReplayStore {
  constructor(private readonly root = "constitutional/cep") {}

  verifyDecision(
    policyVersion: string,
    intent: { id: string; kind: string; agent_id: string },
    decision: { id: string; outcome: string; reason: string }
  ): CslReplayRecord {
    const record: CslReplayRecord = {
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

  comparePolicyVersions(results: Record<string, Array<{ intent_id: string; outcome: string }>>): Array<{
    intent_id: string;
    outcomes: Record<string, string>;
    changed: boolean;
  }> {
    const outcomesByIntent = new Map<string, Record<string, string>>();
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

  getEvents(): CslReplayRecord[] {
    return readJsonl<CslReplayRecord>(replayFile(this.root)).sort((left, right) => {
      const timestampCompare = left.timestamp.localeCompare(right.timestamp);
      if (timestampCompare !== 0) {
        return timestampCompare;
      }
      return left.replay_id.localeCompare(right.replay_id);
    });
  }
}

function createReplayId(policyVersion: string, intentId: string, decisionId: string): string {
  return stableStringify({ policyVersion, intentId, decisionId }).replace(/[^a-zA-Z0-9]+/g, "-").slice(0, 32);
}
