import type { IncomingMessage, ServerResponse } from "http";
import { readLaunchReadinessSpecification } from "../core/specification-governance/registry.js";

function sendJson(res: ServerResponse, statusCode: number, body: unknown): void {
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(body));
}

function isLaunchReadinessRequest(req: IncomingMessage): boolean {
  if (req.method !== "GET" || !req.url) {
    return false;
  }
  try {
    return new URL(req.url, "http://localhost").pathname === "/launch-readiness";
  } catch {
    return false;
  }
}

export async function handleLaunchReadinessRequest(req: IncomingMessage, res: ServerResponse): Promise<boolean> {
  if (!isLaunchReadinessRequest(req)) {
    return false;
  }

  try {
    const readiness = readLaunchReadinessSpecification("constitutional/launch-readiness.json");
    sendJson(res, 200, readiness);
    return true;
  } catch (error) {
    sendJson(res, 500, {
      ok: false,
      error: error instanceof Error ? error.message : String(error)
    });
    return true;
  }
}
