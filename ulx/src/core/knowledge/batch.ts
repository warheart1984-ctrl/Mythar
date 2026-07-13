import { readFileSync } from "fs";
import { FileKnowledgeStore } from "./store.js";
import { KnowledgePipelineAdapter } from "./pipeline.js";
import type {
  KnowledgePipelineItem,
  KnowledgePipelineSummary,
  KnowledgePublicProjection
} from "../../types/knowledge.js";

export interface KnowledgeBatchResult extends KnowledgePipelineSummary {
  projection: KnowledgePublicProjection;
}

function parseBatchPayload(parsed: unknown): KnowledgePipelineItem[] {
  if (Array.isArray(parsed)) {
    return parsed as KnowledgePipelineItem[];
  }
  if (parsed && typeof parsed === "object") {
    const items = (parsed as { items?: unknown }).items;
    if (Array.isArray(items)) {
      return items as KnowledgePipelineItem[];
    }
  }
  throw new Error("batch payload must be an array or an object with an items array");
}

export function loadKnowledgeBatchFile(path: string): KnowledgePipelineItem[] {
  const raw = readFileSync(path, "utf8");
  return parseBatchPayload(JSON.parse(raw) as unknown);
}

export function loadKnowledgeBatchJson(raw: string): KnowledgePipelineItem[] {
  return parseBatchPayload(JSON.parse(raw) as unknown);
}

export function processKnowledgeBatch(items: KnowledgePipelineItem[]): KnowledgeBatchResult {
  const store = new FileKnowledgeStore("constitutional/knowledge");
  const pipeline = new KnowledgePipelineAdapter(store);
  const summary = pipeline.ingestClassifiedBatch(items);
  return {
    ...summary,
    projection: store.projection()
  };
}
