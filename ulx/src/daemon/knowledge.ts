import type { IncomingMessage, ServerResponse } from "http";
import { loadKnowledgeBatchJson, processKnowledgeBatch } from "../core/knowledge/batch.js";

function sendJson(res: ServerResponse, statusCode: number, body: unknown): void {
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(body));
}

function readRequestBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk: Buffer | string) => {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    });
    req.on("end", () => {
      resolve(Buffer.concat(chunks).toString("utf8"));
    });
    req.on("error", (error) => {
      reject(error);
    });
  });
}

function isKnowledgeIngestRequest(req: IncomingMessage): boolean {
  if (req.method !== "POST" || !req.url) {
    return false;
  }
  try {
    return new URL(req.url, "http://localhost").pathname === "/knowledge/ingest";
  } catch {
    return false;
  }
}

export async function handleKnowledgeIngestRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<boolean> {
  if (!isKnowledgeIngestRequest(req)) {
    return false;
  }

  try {
    const raw = await readRequestBody(req);
    if (!raw.trim()) {
      sendJson(res, 400, {
        ok: false,
        error: "missing batch payload"
      });
      return true;
    }

    const items = loadKnowledgeBatchJson(raw);
    const result = processKnowledgeBatch(items);
    sendJson(res, result.valid ? 200 : 422, {
      ok: result.valid,
      processed: result.processed,
      ingested: result.ingested,
      excluded: result.excluded,
      validationIssues: result.validationIssues,
      projection: result.projection
    });
    return true;
  } catch (error) {
    sendJson(res, 400, {
      ok: false,
      error: error instanceof Error ? error.message : String(error)
    });
    return true;
  }
}
