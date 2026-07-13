import type { IncomingMessage, ServerResponse } from "http";
import { readSpecificationDependencyGraph } from "../core/specification-governance/registry.js";

function sendJson(res: ServerResponse, statusCode: number, body: unknown): void {
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(body));
}

function isDependencyGraphRequest(req: IncomingMessage): boolean {
  if (req.method !== "GET" || !req.url) {
    return false;
  }
  try {
    return new URL(req.url, "http://localhost").pathname === "/specification-dependency-graph";
  } catch {
    return false;
  }
}

export async function handleSpecificationDependencyGraphRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<boolean> {
  if (!isDependencyGraphRequest(req)) {
    return false;
  }

  try {
    const graph = readSpecificationDependencyGraph("constitutional/specification-dependency-graph.json");
    sendJson(res, 200, graph);
    return true;
  } catch (error) {
    sendJson(res, 500, {
      ok: false,
      error: error instanceof Error ? error.message : String(error)
    });
    return true;
  }
}
