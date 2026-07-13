import { createServer, type IncomingMessage } from "http";
import { watch, readFileSync, existsSync, readdirSync } from "fs";
import { createHash } from "crypto";
import { fileURLToPath } from "url";
import type { Duplex } from "stream";
import { loadCIEMSChain, validateChain } from "../core/chain.js";
import { handleKnowledgeIngestRequest } from "./knowledge.js";
import { handleLaunchReadinessRequest } from "./launchReadiness.js";
import { handleSpecificationDependencyGraphRequest } from "./specificationDependencyGraph.js";
import { handleSpecificationRegistryRequest } from "./specificationRegistry.js";
import { handleSovereignOsConstitutionalKernelRequest } from "./sovereignOsConstitutionalKernel.js";
import { createAndBroadcastUlxEvent, registerUlxEventSink, serializeUlxEvent, type UlxEvent } from "./events.js";

const ROOT = fileURLToPath(new URL("../..", import.meta.url));
if (process.cwd() !== ROOT) {
  process.chdir(ROOT);
}

const PORT = Number.parseInt(process.env.ULX_DAEMON_PORT || "8080", 10);
const HOST = process.env.ULX_DAEMON_HOST || "127.0.0.1";

const substrates = discoverSubstrates();
const wsClients = new Set<Duplex>();
const lastGovernanceEventByFile = new Map<string, string>();
const lastContinuityEventByFile = new Map<string, string>();

function discoverSubstrates(): string[] {
  const substrateRoot = "substrates";
  if (!existsSync(substrateRoot)) {
    return ["sovereign-os"];
  }
  return readdirSync(substrateRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => existsSync(`substrates/${name}/substrate.json`));
}

function readJsonlTail(path: string): Record<string, unknown> | null {
  if (!existsSync(path)) {
    return null;
  }
  const lines = readFileSync(path, "utf8")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  if (lines.length === 0) {
    return null;
  }
  return JSON.parse(lines[lines.length - 1]) as Record<string, unknown>;
}

function encodeWebSocketFrame(message: string): Buffer {
  const payload = Buffer.from(message, "utf8");
  const length = payload.length;
  if (length < 126) {
    const frame = Buffer.allocUnsafe(2 + length);
    frame[0] = 0x81;
    frame[1] = length;
    payload.copy(frame, 2);
    return frame;
  }
  if (length < 65536) {
    const frame = Buffer.allocUnsafe(4 + length);
    frame[0] = 0x81;
    frame[1] = 126;
    frame.writeUInt16BE(length, 2);
    payload.copy(frame, 4);
    return frame;
  }
  const frame = Buffer.allocUnsafe(10 + length);
  frame[0] = 0x81;
  frame[1] = 127;
  frame.writeBigUInt64BE(BigInt(length), 2);
  payload.copy(frame, 10);
  return frame;
}

function acceptWebSocket(req: IncomingMessage, socket: Duplex): void {
  const key = req.headers["sec-websocket-key"];
  if (typeof key !== "string") {
    socket.destroy();
    return;
  }
  const accept = createHash("sha1")
    .update(`${key}258EAFA5-E914-47DA-95CA-C5AB0DC85B11`)
    .digest("base64");
  socket.write(
    [
      "HTTP/1.1 101 Switching Protocols",
      "Upgrade: websocket",
      "Connection: Upgrade",
      `Sec-WebSocket-Accept: ${accept}`,
      "",
      ""
    ].join("\r\n")
  );
  wsClients.add(socket);
  socket.on("close", () => {
    wsClients.delete(socket);
  });
  socket.on("error", () => {
    wsClients.delete(socket);
  });
}

function broadcastEvent(event: UlxEvent): void {
  const message = serializeUlxEvent(event);
  for (const socket of wsClients) {
    try {
      socket.write(encodeWebSocketFrame(message));
    } catch {
      wsClients.delete(socket);
    }
  }
}

registerUlxEventSink((event) => {
  broadcastEvent(event);
});

function broadcastFromGovernanceLog(substrateId: string): void {
  const path = `logs/governance/${substrateId}.log.jsonl`;
  const entry = readJsonlTail(path);
  if (!entry) {
    return;
  }
  const eventId = String(entry.event_id ?? "");
  if (!eventId || lastGovernanceEventByFile.get(path) === eventId) {
    return;
  }
  lastGovernanceEventByFile.set(path, eventId);
  const result = String(entry.result ?? "");
  if (result === "requested" || result === "approved" || result === "blocked") {
    const kind =
      result === "requested"
        ? "decision.requested"
        : result === "approved"
          ? "decision.approved"
          : "decision.blocked";
    const payload =
      result === "requested"
        ? {
            decision_id: String(entry.decision_id ?? ""),
            type: String(entry.type ?? ""),
            actor: String(entry.actor ?? ""),
            target_status: entry.target_status ? String(entry.target_status) : undefined,
            reason: entry.reason ? String(entry.reason) : undefined
          }
        : result === "approved"
          ? {
              decision_id: String(entry.decision_id ?? ""),
              type: String(entry.type ?? ""),
              actor: String(entry.actor ?? ""),
              target_status: entry.target_status ? String(entry.target_status) : undefined
            }
          : {
              decision_id: String(entry.decision_id ?? ""),
              type: String(entry.type ?? ""),
              actor: String(entry.actor ?? ""),
              error: String(entry.error ?? "UNKNOWN")
            };
    createAndBroadcastUlxEvent(
      String(entry.substrate_id ?? substrateId),
      kind,
      payload,
      String(entry.timestamp ?? new Date().toISOString())
    );
  }
}

function broadcastFromContinuity(substrateId: string): void {
  const path = `constitutional/continuity/${substrateId}.continuity.json`;
  if (!existsSync(path)) {
    return;
  }
  const continuity = JSON.parse(readFileSync(path, "utf8")) as {
    timeline?: Array<{ event_id: string; type: string; timestamp: string; details?: string }>;
  };
  const last = continuity.timeline?.[continuity.timeline.length - 1];
  if (!last) {
    return;
  }
  if (lastContinuityEventByFile.get(path) === last.event_id) {
    return;
  }
  lastContinuityEventByFile.set(path, last.event_id);
  createAndBroadcastUlxEvent(
    substrateId,
    "continuity.appended",
    {
      event_id: last.event_id,
      type: last.type,
      timestamp: last.timestamp,
      details: last.details
    },
    last.timestamp
  );
}

function validateAll(): void {
  for (const id of substrates) {
    try {
      const chain = loadCIEMSChain(id);
      const ok = validateChain(chain);
      createAndBroadcastUlxEvent(
        id,
        ok ? "chain.validated" : "chain.invalid",
        ok
          ? {
              valid: true,
              intent_id: chain.intent.intent,
              evidence_id: String(chain.evidence.artifacts.length),
              authority_id: chain.authority.mandate,
              continuity_id: chain.continuity.timeline[chain.continuity.timeline.length - 1]?.event_id ?? ""
            }
          : {
              valid: false,
              reason: "CIEMS_CHAIN_INVALID"
            },
        new Date().toISOString()
      );
      console.log(`[ULX] Chain ${id}: ${ok ? "VALID" : "INVALID"}`);
    } catch (error) {
      console.error(`[ULX] Chain ${id}: ERROR`, error);
      createAndBroadcastUlxEvent(
        id,
        "daemon.error",
        {
          message: error instanceof Error ? error.message : String(error),
          stack: error instanceof Error ? error.stack : undefined
        },
        new Date().toISOString()
      );
    }
  }
}

function startHttpServer(): void {
  const server = createServer((req, res) => {
    void (async () => {
      if (await handleLaunchReadinessRequest(req, res)) {
        return;
      }
      if (await handleSovereignOsConstitutionalKernelRequest(req, res)) {
        return;
      }
      if (await handleSpecificationDependencyGraphRequest(req, res)) {
        return;
      }
      if (await handleSpecificationRegistryRequest(req, res)) {
        return;
      }
      if (await handleKnowledgeIngestRequest(req, res)) {
        return;
      }
      if (!req.url) {
        res.statusCode = 400;
        res.end("missing url");
        return;
      }
      if (req.url === "/health") {
        res.setHeader("content-type", "application/json");
        res.end(
          JSON.stringify({
            ok: true,
            substrates: substrates.length,
            port: PORT
          })
        );
        return;
      }
      res.statusCode = 404;
      res.end("not found");
    })()
      .catch((error) => {
        res.statusCode = 500;
        res.setHeader("content-type", "application/json");
        res.end(
          JSON.stringify({
            ok: false,
            error: error instanceof Error ? error.message : String(error)
          })
        );
      });
  });

  server.on("upgrade", (req, socket, head) => {
    if (req.url !== "/events") {
      socket.destroy();
      return;
    }
    if (head.length > 0) {
      socket.write(head);
    }
    acceptWebSocket(req, socket);
  });

  server.listen(PORT, HOST, () => {
    console.log(`[ULX] Daemon started on ws://${HOST}:${PORT}/events`);
  });
}

function startWatchers(): void {
  if (existsSync("constitutional")) {
    watch("constitutional", { recursive: true }, (_eventType, filename) => {
      if (typeof filename === "string" && filename.includes("continuity")) {
        const substrateId = filename.split(/[\\/]/).filter(Boolean).find((part) => part.endsWith(".continuity.json"));
        if (substrateId) {
          broadcastFromContinuity(substrateId.replace(".continuity.json", ""));
        }
      }
      validateAll();
    });
  }

  if (existsSync("logs/governance")) {
    watch("logs/governance", { recursive: true }, (_eventType, filename) => {
      if (typeof filename !== "string") {
        return;
      }
      const match = filename.match(/^([^.]+)\.log\.jsonl$/);
      if (match) {
        broadcastFromGovernanceLog(match[1]);
      }
    });
  }
}

export function startDaemon(): void {
  startHttpServer();
  validateAll();
  startWatchers();
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  startDaemon();
}
