import { existsSync } from "fs";
import { loadKnowledgeBatchFile, processKnowledgeBatch } from "../../core/knowledge/batch.js";
import type { KnowledgeBatchResult } from "../../core/knowledge/batch.js";

export function knowledgeIngest(batchPath: string): number {
  if (!batchPath) {
    console.error("Usage: knowledge-ingest <batch_json>");
    return 1;
  }
  if (!existsSync(batchPath)) {
    console.error(`Batch file not found: ${batchPath}`);
    return 1;
  }

  let summary: KnowledgeBatchResult;
  try {
    summary = processKnowledgeBatch(loadKnowledgeBatchFile(batchPath));
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    return 1;
  }

  console.log(
    JSON.stringify(
      {
        ok: summary.valid,
        processed: summary.processed,
        ingested: summary.ingested,
        excluded: summary.excluded,
        validationIssues: summary.validationIssues,
        projection: summary.projection
      },
      null,
      2
    )
  );

  return summary.valid ? 0 : 1;
}
