import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import type {
  KnowledgeClassificationResult,
  KnowledgeClaim,
  KnowledgeClaimDocumentEdge,
  KnowledgeClaimEntityEdge,
  KnowledgeDocument,
  KnowledgeDocumentEntityEdge,
  KnowledgeDisposition,
  KnowledgeEntity,
  KnowledgeExclusion,
  KnowledgeGraph,
  KnowledgeGraphEdge,
  KnowledgeGraphNode,
  KnowledgeHarvestCandidate,
  KnowledgePublicProjection,
  KnowledgeStage,
  KnowledgeRole,
  KnowledgeStore
} from "../../types/knowledge.js";

function ensureDirectory(path: string): void {
  const dir = dirname(path);
  if (dir && !existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function writeJson(path: string, data: unknown): void {
  ensureDirectory(path);
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function appendJsonl(path: string, data: unknown): void {
  ensureDirectory(path);
  appendFileSync(path, `${JSON.stringify(data)}\n`, "utf8");
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

function currentTimestamp(): string {
  return new Date().toISOString();
}

function stableId(parts: string[]): string {
  const seed = parts.join("|");
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) >>> 0;
  }
  return hash.toString(16).padStart(8, "0");
}

function documentPath(root: string): string {
  return join(root, "documents.jsonl");
}

function entityPath(root: string): string {
  return join(root, "entities.jsonl");
}

function claimPath(root: string): string {
  return join(root, "claims.jsonl");
}

function documentEntityPath(root: string): string {
  return join(root, "document-entities.jsonl");
}

function claimDocumentPath(root: string): string {
  return join(root, "claim-documents.jsonl");
}

function claimEntityPath(root: string): string {
  return join(root, "claim-entities.jsonl");
}

function exclusionPath(root: string): string {
  return join(root, "exclusions.jsonl");
}

function documentId(candidate: KnowledgeHarvestCandidate): string {
  const sourceKey = candidate.source_identifier || candidate.identifiers[0]?.id_value || candidate.title;
  return `DOC_${stableId([candidate.harvest_source, sourceKey, candidate.title])}`;
}

function validateClassification(classification: KnowledgeClassificationResult): string | null {
  if (!["on_topic", "off_topic", "uncertain"].includes(classification.disposition)) {
    return "invalid disposition";
  }
  if (classification.confidence < 0 || classification.confidence > 1) {
    return "confidence out of range";
  }
  if (!classification.reason.trim()) {
    return "missing relevance reason";
  }
  return null;
}

function entityKey(axis: string, entityId: string): string {
  return `${axis}:${entityId}`;
}

function documentNode(document: KnowledgeDocument): KnowledgeGraphNode {
  return {
    id: document.id,
    kind: "document",
    label: document.title
  };
}

function entityNode(entity: KnowledgeEntity): KnowledgeGraphNode {
  return {
    id: entityKey(entity.axis, entity.id),
    kind: "entity",
    label: entity.canonical_name,
    axis: entity.axis
  };
}

function claimNode(claim: KnowledgeClaim): KnowledgeGraphNode {
  return {
    id: claim.id,
    kind: "claim",
    label: claim.claim_type
  };
}

function edgeDocumentEntity(edge: KnowledgeDocumentEntityEdge): KnowledgeGraphEdge {
  return {
    from: edge.document_id,
    to: entityKey(edge.axis, edge.entity_id),
    type: "document_entity",
    role: edge.role
  };
}

function edgeClaimDocument(edge: KnowledgeClaimDocumentEdge): KnowledgeGraphEdge {
  return {
    from: edge.claim_id,
    to: edge.document_id,
    type: "claim_document",
    role: edge.role
  };
}

function edgeClaimEntity(edge: KnowledgeClaimEntityEdge): KnowledgeGraphEdge {
  return {
    from: edge.claim_id,
    to: entityKey(edge.axis, edge.entity_id),
    type: "claim_entity",
    role: edge.role
  };
}

export class FileKnowledgeStore implements KnowledgeStore {
  constructor(private readonly root = "constitutional/knowledge") {}

  upsertEntity(entity: KnowledgeEntity): KnowledgeEntity {
    const entities = this.listEntities();
    const next = [...entities.filter((entry) => !(entry.axis === entity.axis && entry.id === entity.id)), entity];
    appendJsonl(entityPath(this.root), entity);
    return entity;
  }

  listEntities(axis?: string): KnowledgeEntity[] {
    const entities = readJsonl<KnowledgeEntity>(entityPath(this.root));
    const filtered = axis ? entities.filter((entity) => entity.axis === axis) : entities;
    const seen = new Map<string, KnowledgeEntity>();
    for (const entity of filtered) {
      seen.set(entityKey(entity.axis, entity.id), entity);
    }
    return [...seen.values()].sort((left, right) => {
      const axisCompare = left.axis.localeCompare(right.axis);
      if (axisCompare !== 0) {
        return axisCompare;
      }
      return left.id.localeCompare(right.id);
    });
  }

  ingestCandidate(
    candidate: KnowledgeHarvestCandidate,
    classification: KnowledgeClassificationResult
  ): KnowledgeDocument | KnowledgeExclusion {
    const validationIssue = validateClassification(classification);
    if (validationIssue) {
      throw new Error(validationIssue);
    }

    const docId = documentId(candidate);
    const title = candidate.title.trim();
    const hasTag = classification.entityAssignments.length > 0;
    const disposition = classification.disposition;
    if (disposition === "off_topic") {
      return this.recordExclusion(candidate, "relevance_off_topic", classification.reason);
    }
    if (disposition === "uncertain") {
      return this.recordExclusion(candidate, "uncertain_insufficient_data", classification.reason);
    }
    if (!hasTag) {
      return this.recordExclusion(candidate, "no_relevant_tag", classification.reason);
    }

    const entityIndex = new Map(this.listEntities().map((entity) => [entityKey(entity.axis, entity.id), entity] as const));
    const edges: KnowledgeDocumentEntityEdge[] = [];
    for (const assignment of classification.entityAssignments) {
      const entity = entityIndex.get(entityKey(assignment.axis, assignment.entity_id));
      if (!entity) {
        continue;
      }
      edges.push({
        document_id: docId,
        entity_id: entity.id,
        axis: entity.axis,
        role: assignment.role
      });
    }
    if (edges.length === 0) {
      return this.recordExclusion(candidate, "no_relevant_tag", classification.reason);
    }

    const document: KnowledgeDocument = {
      id: docId,
      title,
      abstract: candidate.abstract,
      body: undefined,
      source: candidate.harvest_source,
      harvest_source: candidate.harvest_source,
      discovery_method: candidate.discovery_method,
      harvest_query: candidate.harvest_query,
      harvested_at: currentTimestamp(),
      updated_at: currentTimestamp(),
      review_state: "unaudited",
      relevance_verdict: disposition,
      relevance_confidence: classification.confidence,
      relevance_reason: classification.reason,
      raw_source_ref: candidate.source_identifier,
      identifiers: candidate.identifiers,
      metadata: {
        source_identifier: candidate.source_identifier,
        matched_entities: candidate.matched_entities,
        species_format: classification.speciesFormat ?? null,
        original_metadata: candidate.metadata
      }
    };

    appendJsonl(documentPath(this.root), document);
    for (const edge of edges) {
      appendJsonl(documentEntityPath(this.root), edge);
    }
    return document;
  }

  addClaim(claim: KnowledgeClaim): KnowledgeClaim {
    appendJsonl(claimPath(this.root), claim);
    return claim;
  }

  linkClaimDocument(edge: KnowledgeClaimDocumentEdge): KnowledgeClaimDocumentEdge {
    appendJsonl(claimDocumentPath(this.root), edge);
    return edge;
  }

  linkClaimEntity(edge: KnowledgeClaimEntityEdge): KnowledgeClaimEntityEdge {
    appendJsonl(claimEntityPath(this.root), edge);
    return edge;
  }

  listDocuments(): KnowledgeDocument[] {
    return readJsonl<KnowledgeDocument>(documentPath(this.root)).sort((left, right) =>
      left.id.localeCompare(right.id)
    );
  }

  listClaims(): KnowledgeClaim[] {
    return readJsonl<KnowledgeClaim>(claimPath(this.root)).sort((left, right) =>
      left.id.localeCompare(right.id)
    );
  }

  listExclusions(): KnowledgeExclusion[] {
    return readJsonl<KnowledgeExclusion>(exclusionPath(this.root)).sort((left, right) =>
      left.id.localeCompare(right.id)
    );
  }

  documentEdges(): KnowledgeDocumentEntityEdge[] {
    return readJsonl<KnowledgeDocumentEntityEdge>(documentEntityPath(this.root));
  }

  claimDocumentEdges(): KnowledgeClaimDocumentEdge[] {
    return readJsonl<KnowledgeClaimDocumentEdge>(claimDocumentPath(this.root));
  }

  claimEntityEdges(): KnowledgeClaimEntityEdge[] {
    return readJsonl<KnowledgeClaimEntityEdge>(claimEntityPath(this.root));
  }

  validate(): { valid: boolean; issues: string[] } {
    const issues: string[] = [];
    const documents = this.listDocuments();
    const entities = this.listEntities();
    const claims = this.listClaims();
    const exclusions = this.listExclusions();
    const entitySet = new Set(entities.map((entity) => entityKey(entity.axis, entity.id)));

    for (const document of documents) {
      if (!document.id.startsWith("DOC_")) {
        issues.push(`document ${document.id} has invalid canonical id`);
      }
      if (document.relevance_verdict === "on_topic") {
        const linked = this.documentEdges().filter((edge) => edge.document_id === document.id);
        if (linked.length === 0) {
          issues.push(`document ${document.id} is on_topic without entity links`);
        }
      }
    }

    for (const edge of this.documentEdges()) {
      if (!entitySet.has(entityKey(edge.axis, edge.entity_id))) {
        issues.push(`document edge references unknown entity ${edge.axis}:${edge.entity_id}`);
      }
    }

    for (const edge of this.claimEntityEdges()) {
      if (!entitySet.has(entityKey(edge.axis, edge.entity_id))) {
        issues.push(`claim edge references unknown entity ${edge.axis}:${edge.entity_id}`);
      }
    }

    for (const claim of claims) {
      const docs = this.claimDocumentEdges().filter((edge) => edge.claim_id === claim.id);
      if (docs.length === 0) {
        issues.push(`claim ${claim.id} has no source documents`);
      }
    }

    for (const exclusion of exclusions) {
      if (!exclusion.reason.trim()) {
        issues.push(`exclusion ${exclusion.id} missing reason`);
      }
    }

    return {
      valid: issues.length === 0,
      issues
    };
  }

  projection(): KnowledgePublicProjection {
    const entities = this.listEntities();
    const entityLookup = new Map(entities.map((entity) => [entityKey(entity.axis, entity.id), entity] as const));
    const documents = this.listDocuments().map((document) => {
      const documentEntities = this.documentEdges()
        .filter((edge) => edge.document_id === document.id)
        .map((edge) => {
          const entity = entityLookup.get(entityKey(edge.axis, edge.entity_id));
          return entity
            ? {
                axis: entity.axis,
                entity_id: entity.id,
                canonical_name: entity.canonical_name,
                role: edge.role
              }
            : null;
        })
        .filter(Boolean) as KnowledgePublicProjection["documents"][number]["entities"];
      return {
        id: document.id,
        title: document.title,
        source: document.source,
        harvested_at: document.harvested_at,
        updated_at: document.updated_at,
        identifiers: [...document.identifiers],
        entities: documentEntities
      };
    });

    const claims = this.listClaims().map((claim) => {
      const docs = this.claimDocumentEdges()
        .filter((edge) => edge.claim_id === claim.id)
        .map((edge) => ({ document_id: edge.document_id, role: edge.role }));
      const linkedEntities = this.claimEntityEdges()
        .filter((edge) => edge.claim_id === claim.id)
        .map((edge) => {
          const entity = entityLookup.get(entityKey(edge.axis, edge.entity_id));
          return entity
            ? {
                axis: entity.axis,
                entity_id: entity.id,
                canonical_name: entity.canonical_name,
                role: edge.role
              }
            : null;
        })
        .filter(Boolean) as KnowledgePublicProjection["claims"][number]["entities"];
      return {
        id: claim.id,
        text: claim.text,
        claim_type: claim.claim_type,
        confidence: claim.confidence,
        documents: docs,
        entities: linkedEntities
      };
    });

    return {
      entities,
      documents,
      claims
    };
  }

  graph(): KnowledgeGraph {
    const documents = this.listDocuments();
    const claims = this.listClaims();
    const entities = this.listEntities();
    const nodes: KnowledgeGraphNode[] = [
      ...documents.map(documentNode),
      ...entities.map(entityNode),
      ...claims.map(claimNode)
    ];
    const edges: KnowledgeGraphEdge[] = [
      ...this.documentEdges().map(edgeDocumentEntity),
      ...this.claimDocumentEdges().map(edgeClaimDocument),
      ...this.claimEntityEdges().map(edgeClaimEntity)
    ];
    return { nodes, edges };
  }

  private recordExclusion(
    candidate: KnowledgeHarvestCandidate,
    stage: KnowledgeStage,
    reason: string
  ): KnowledgeExclusion {
    const exclusion: KnowledgeExclusion = {
      id: `EXCL_${stableId([candidate.harvest_source, candidate.source_identifier, candidate.title, stage])}`,
      source_identifier: candidate.source_identifier,
      title: candidate.title,
      stage,
      reason,
      harvest_source: candidate.harvest_source,
      harvest_query: candidate.harvest_query,
      excluded_at: currentTimestamp()
    };
    appendJsonl(exclusionPath(this.root), exclusion);
    return exclusion;
  }
}
