export type KnowledgeDisposition = "on_topic" | "off_topic" | "uncertain";

export type KnowledgeRole = "primary" | "secondary";

export type KnowledgeClaimRole = "supports" | "contradicts" | "partially_supports";

export type KnowledgeStage =
  | "relevance_off_topic"
  | "uncertain_insufficient_data"
  | "no_relevant_tag";

export interface KnowledgeDocumentIdentifier {
  id_type: string;
  id_value: string;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  abstract?: string;
  body?: string;
  source: string;
  harvest_source: string;
  discovery_method: string;
  harvest_query: string;
  harvested_at: string;
  updated_at: string;
  review_state: "unaudited" | "flagged" | "audited";
  relevance_verdict: KnowledgeDisposition;
  relevance_confidence: number;
  relevance_reason: string;
  raw_source_ref: string;
  identifiers: KnowledgeDocumentIdentifier[];
  metadata: Record<string, unknown>;
}

export interface KnowledgeEntity {
  id: string;
  axis: string;
  canonical_name: string;
  aliases: string[];
  status: "active" | "deprecated" | "draft";
  metadata: Record<string, unknown>;
}

export interface KnowledgeDocumentEntityEdge {
  document_id: string;
  entity_id: string;
  axis: string;
  role: KnowledgeRole;
}

export interface KnowledgeClaim {
  id: string;
  text: string;
  claim_type: string;
  confidence: number;
  review_state: "unaudited" | "flagged" | "audited";
  synthesis_rationale: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface KnowledgeClaimDocumentEdge {
  claim_id: string;
  document_id: string;
  role: KnowledgeClaimRole;
}

export interface KnowledgeClaimEntityEdge {
  claim_id: string;
  entity_id: string;
  axis: string;
  role: KnowledgeRole;
}

export interface KnowledgeExclusion {
  id: string;
  source_identifier: string;
  title: string;
  stage: KnowledgeStage;
  reason: string;
  harvest_source: string;
  harvest_query: string;
  excluded_at: string;
}

export interface KnowledgeClassificationResult {
  disposition: KnowledgeDisposition;
  confidence: number;
  reason: string;
  entityAssignments: Array<{
    axis: string;
    entity_id: string;
    role: KnowledgeRole;
  }>;
  speciesFormat?: string;
}

export interface KnowledgeHarvestCandidate {
  source_identifier: string;
  title: string;
  abstract?: string;
  metadata: Record<string, unknown>;
  identifiers: KnowledgeDocumentIdentifier[];
  harvest_source: string;
  discovery_method: string;
  harvest_query: string;
  matched_entities: Array<{
    axis: string;
    entity_id: string;
  }>;
}

export interface KnowledgeClassifier {
  classify(
    candidate: KnowledgeHarvestCandidate,
    allowedEntities: KnowledgeEntity[]
  ): KnowledgeClassificationResult;
}

export interface KnowledgePipelineItem {
  candidate: KnowledgeHarvestCandidate;
  classification: KnowledgeClassificationResult;
}

export interface KnowledgePipelineResult {
  candidate_id: string;
  disposition: "document" | "exclusion";
  record: KnowledgeDocument | KnowledgeExclusion;
}

export interface KnowledgePipelineSummary {
  processed: number;
  ingested: number;
  excluded: number;
  valid: boolean;
  validationIssues: string[];
}

export interface KnowledgePublicDocument {
  id: string;
  title: string;
  source: string;
  harvested_at: string;
  updated_at: string;
  identifiers: KnowledgeDocumentIdentifier[];
  entities: Array<{
    axis: string;
    entity_id: string;
    canonical_name: string;
    role: KnowledgeRole;
  }>;
}

export interface KnowledgePublicClaim {
  id: string;
  text: string;
  claim_type: string;
  confidence: number;
  documents: Array<{ document_id: string; role: KnowledgeClaimRole }>;
  entities: Array<{
    axis: string;
    entity_id: string;
    canonical_name: string;
    role: KnowledgeRole;
  }>;
}

export interface KnowledgePublicProjection {
  entities: KnowledgeEntity[];
  documents: KnowledgePublicDocument[];
  claims: KnowledgePublicClaim[];
}

export interface KnowledgeGraphNode {
  id: string;
  kind: "document" | "entity" | "claim";
  label: string;
  axis?: string;
  role?: KnowledgeRole | KnowledgeClaimRole;
}

export interface KnowledgeGraphEdge {
  from: string;
  to: string;
  type: "document_entity" | "claim_document" | "claim_entity";
  role?: KnowledgeRole | KnowledgeClaimRole;
}

export interface KnowledgeGraph {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

export interface KnowledgeStore {
  upsertEntity(entity: KnowledgeEntity): KnowledgeEntity;
  listEntities(axis?: string): KnowledgeEntity[];
  ingestCandidate(candidate: KnowledgeHarvestCandidate, classification: KnowledgeClassificationResult): KnowledgeDocument | KnowledgeExclusion;
  addClaim(claim: KnowledgeClaim): KnowledgeClaim;
  linkClaimDocument(edge: KnowledgeClaimDocumentEdge): KnowledgeClaimDocumentEdge;
  linkClaimEntity(edge: KnowledgeClaimEntityEdge): KnowledgeClaimEntityEdge;
  listDocuments(): KnowledgeDocument[];
  listClaims(): KnowledgeClaim[];
  listExclusions(): KnowledgeExclusion[];
  documentEdges(): KnowledgeDocumentEntityEdge[];
  claimDocumentEdges(): KnowledgeClaimDocumentEdge[];
  claimEntityEdges(): KnowledgeClaimEntityEdge[];
  validate(): { valid: boolean; issues: string[] };
  projection(): KnowledgePublicProjection;
  graph(): KnowledgeGraph;
}
