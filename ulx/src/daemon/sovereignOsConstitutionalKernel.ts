import type { IncomingMessage, ServerResponse } from "http";
import { readSovereignOsConstitutionalKernelRegistryModel } from "../core/specification-governance/registry.js";

function sendJson(res: ServerResponse, statusCode: number, body: unknown): void {
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(body));
}

function isSovereignOsConstitutionalKernelRequest(req: IncomingMessage): boolean {
  if (req.method !== "GET" || !req.url) {
    return false;
  }
  try {
    return new URL(req.url, "http://localhost").pathname === "/sovereign-os-constitutional-kernel";
  } catch {
    return false;
  }
}

export async function handleSovereignOsConstitutionalKernelRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<boolean> {
  if (!isSovereignOsConstitutionalKernelRequest(req)) {
    return false;
  }

  try {
    const kernel = readSovereignOsConstitutionalKernelRegistryModel(
      "constitutional/sovereign-os-constitutional-kernel.registry-model.json"
    );
    sendJson(res, 200, kernel);
    return true;
  } catch (error) {
    sendJson(res, 500, {
      ok: false,
      error: error instanceof Error ? error.message : String(error)
    });
    return true;
  }
}
