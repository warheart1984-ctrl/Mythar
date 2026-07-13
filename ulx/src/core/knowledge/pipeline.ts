import type {
  KnowledgeClassifier,
  KnowledgeHarvestCandidate,
  KnowledgePipelineItem,
  KnowledgePipelineResult,
  KnowledgePipelineSummary,
  KnowledgeStore
} from "../../types/knowledge.js";

function candidateId(candidate: KnowledgeHarvestCandidate): string {
  return candidate.source_identifier || candidate.identifiers[0]?.id_value || candidate.title;
}

export class KnowledgePipelineAdapter {
  constructor(private readonly store: KnowledgeStore) {}

  classify(
    candidate: KnowledgeHarvestCandidate,
    classifier: KnowledgeClassifier
  ) {
    const allowedEntities = this.store.listEntities();
    return classifier.classify(candidate, allowedEntities);
  }

  ingest(
    candidate: KnowledgeHarvestCandidate,
    classifier: KnowledgeClassifier
  ): KnowledgePipelineResult {
    const classification = this.classify(candidate, classifier);
    const record = this.store.ingestCandidate(candidate, classification);
    return {
      candidate_id: candidateId(candidate),
      disposition: "stage" in record ? "exclusion" : "document",
      record
    };
  }

  ingestClassified(
    item: KnowledgePipelineItem
  ): KnowledgePipelineResult {
    const record = this.store.ingestCandidate(item.candidate, item.classification);
    return {
      candidate_id: candidateId(item.candidate),
      disposition: "stage" in record ? "exclusion" : "document",
      record
    };
  }

  ingestClassifiedBatch(items: KnowledgePipelineItem[]): KnowledgePipelineSummary {
    let ingested = 0;
    let excluded = 0;
    for (const item of items) {
      const result = this.ingestClassified(item);
      if (result.disposition === "document") {
        ingested += 1;
      } else {
        excluded += 1;
      }
    }
    const validation = this.store.validate();
    return {
      processed: items.length,
      ingested,
      excluded,
      valid: validation.valid,
      validationIssues: validation.issues
    };
  }

  ingestBatch(
    candidates: KnowledgeHarvestCandidate[],
    classifier: KnowledgeClassifier
  ): KnowledgePipelineSummary {
    let ingested = 0;
    let excluded = 0;
    for (const candidate of candidates) {
      const result = this.ingest(candidate, classifier);
      if (result.disposition === "document") {
        ingested += 1;
      } else {
        excluded += 1;
      }
    }
    const validation = this.store.validate();
    return {
      processed: candidates.length,
      ingested,
      excluded,
      valid: validation.valid,
      validationIssues: validation.issues
    };
  }
}
