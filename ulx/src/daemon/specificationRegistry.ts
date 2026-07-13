import type { IncomingMessage, ServerResponse } from "http";
import { readSpecificationRegistry } from "../core/specification-governance/registry.js";

function sendJson(res: ServerResponse, statusCode: number, body: unknown): void {
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(body));
}

function isRegistryRequest(req: IncomingMessage): boolean {
  if (req.method !== "GET" || !req.url) {
    return false;
  }
  try {
    return new URL(req.url, "http://localhost").pathname === "/specification-registry";
  } catch {
    return false;
  }
}

export async function handleSpecificationRegistryRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<boolean> {
  if (!isRegistryRequest(req)) {
    return false;
  }

  try {
    const registry = readSpecificationRegistry("constitutional/specification-registry.json");
    sendJson(res, 200, registry);
    return true;
  } catch (error) {
    sendJson(res, 500, {
      ok: false,
      error: error instanceof Error ? error.message : String(error)
    });
    return true;
  }
}
