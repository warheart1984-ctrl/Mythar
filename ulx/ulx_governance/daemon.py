from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .core import ULXGovernanceStore, discover_repo_root, governance_error


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")


class ULXRequestHandler(BaseHTTPRequestHandler):
    server_version = "ULXDaemon/0.1"

    @property
    def store(self) -> ULXGovernanceStore:
        return self.server.store  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send_json(self, status: int, payload: Any) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, error: dict[str, Any]) -> None:
        self._send_json(status, error)

    def _read_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        if not raw.strip():
            return {}
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def _path_parts(self) -> list[str]:
        parsed = urlparse(self.path)
        return [part for part in parsed.path.split("/") if part]

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlparse(self.path).query)

    def do_GET(self) -> None:  # noqa: N802
        parts = self._path_parts()
        if parts == ["ulx", "api", "substrates"]:
            self._send_json(HTTPStatus.OK, {"ok": True, "substrates": self.store.list_substrates()})
            return
        if len(parts) == 4 and parts[:3] == ["ulx", "api", "substrates"]:
            substrate_id = parts[3]
            self._send_json(HTTPStatus.OK, self.store.substrate_detail(substrate_id))
            return
        if len(parts) == 5 and parts[:3] == ["ulx", "api", "substrates"] and parts[4] == "chain":
            self._send_json(HTTPStatus.OK, self.store.chain_validation_report(parts[3]))
            return
        if len(parts) == 5 and parts[:3] == ["ulx", "api", "substrates"] and parts[4] == "continuity":
            self._send_json(HTTPStatus.OK, self.store.continuity_record(parts[3]))
            return
        if len(parts) == 5 and parts[:3] == ["ulx", "api", "substrates"] and parts[4] == "lineage":
            self._send_json(HTTPStatus.OK, self.store.lineage_graph(parts[3]))
            return
        if len(parts) == 5 and parts[:3] == ["ulx", "api", "logs"] and parts[3] == "governance":
            substrate_id = parts[4]
            self._send_json(HTTPStatus.OK, self.store.decision_log(substrate_id))
            return
        if len(parts) == 3 and parts[:2] == ["ulx", "events"]:
            self._stream_events(parts[2], self._query())
            return
        if len(parts) == 4 and parts[:2] == ["ulx", "events"]:
            self._stream_events(parts[2], {"substrate_id": [parts[3]]})
            return
        self._send_error(
            HTTPStatus.NOT_FOUND,
            governance_error(
                error_type="runtime-invariant-violation",
                severity="error",
                decision_id="daemon:get",
                substrate_id="unknown",
                code="RUNTIME_INVARIANT_BREACH",
                message=f"unknown route: {self.path}",
                details={"path": self.path},
            ),
        )

    def do_POST(self) -> None:  # noqa: N802
        parts = self._path_parts()
        try:
            body = self._read_body()
        except Exception as exc:
            self._send_error(
                HTTPStatus.BAD_REQUEST,
                governance_error(
                    error_type="runtime-invariant-violation",
                    severity="error",
                    decision_id="daemon:body",
                    substrate_id="unknown",
                    code="RUNTIME_INVARIANT_BREACH",
                    message=str(exc),
                    details={"path": self.path},
                ),
            )
            return

        if len(parts) == 5 and parts[:3] == ["ulx", "api", "substrates"] and parts[4] == "decisions":
            report = self.store.submit_decision(parts[3], body, source="daemon")
            status = HTTPStatus.OK if report.get("result") == "approved" else HTTPStatus.BAD_REQUEST
            self._send_json(status, report)
            return
        if len(parts) == 5 and parts[:3] == ["ulx", "api", "substrates"] and parts[4] == "replay":
            report = self.store.replay(
                parts[3],
                from_stage=str(body.get("from", "origin")),
                to_stage=str(body.get("to", "current")),
                mode=str(body.get("mode", "dry-run")),
            )
            self._send_json(HTTPStatus.OK, report)
            return
        self._send_error(
            HTTPStatus.NOT_FOUND,
            governance_error(
                error_type="runtime-invariant-violation",
                severity="error",
                decision_id="daemon:post",
                substrate_id="unknown",
                code="RUNTIME_INVARIANT_BREACH",
                message=f"unknown route: {self.path}",
                details={"path": self.path},
            ),
        )

    def _stream_events(self, kind: str, query: dict[str, list[str]]) -> None:
        substrate_id = query.get("substrate_id", [""])[0] or ""
        if not substrate_id:
            self._send_error(
                HTTPStatus.BAD_REQUEST,
                governance_error(
                    error_type="runtime-invariant-violation",
                    severity="error",
                    decision_id="daemon:events",
                    substrate_id="unknown",
                    code="RUNTIME_INVARIANT_BREACH",
                    message="substrate_id query parameter is required",
                    details={"kind": kind},
                ),
            )
            return
        if kind == "governance":
            payload = self.store.decision_log(substrate_id)["entries"]
        elif kind == "continuity":
            payload = self.store.continuity_timeline(substrate_id)["timeline"]
        elif kind == "replay":
            payload = self.store.replay(substrate_id)["steps"]
        else:
            payload = []
        body_lines = []
        for entry in payload:
            body_lines.append(f"event: {kind}")
            body_lines.append("data: " + json.dumps(entry, sort_keys=True, ensure_ascii=False))
            body_lines.append("")
        if not body_lines:
            body_lines.extend([f"event: {kind}", "data: {}", ""])
        body = "\n".join(body_lines).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ULXThreadingHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], store: ULXGovernanceStore):
        super().__init__(server_address, ULXRequestHandler)
        self.store = store


def serve(repo_root: Path | None = None, host: str = "127.0.0.1", port: int = 8799) -> None:
    store = ULXGovernanceStore(repo_root or discover_repo_root())
    server = ULXThreadingHTTPServer((host, port), store)
    try:
        print(json.dumps({"ok": True, "host": host, "port": port, "repo_root": str(store.repo_root)}, indent=2))
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
