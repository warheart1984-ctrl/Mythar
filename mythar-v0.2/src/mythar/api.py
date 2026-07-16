from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .core import MytharCompiler, REGISTRY_DIR


def serve(port: int, host: str = "127.0.0.1") -> None:
    compiler = MytharCompiler()
    compiler_v3 = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json")
    api_keys = {key.strip() for key in os.getenv("MYTHAR_API_KEYS", "").split(",") if key.strip()}
    rate_limit = int(os.getenv("MYTHAR_RATE_LIMIT", "60"))
    requests: dict[str, list[float]] = {}

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status: int, payload: dict) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Mythar-API-Version", "v1")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())

        def authorized(self) -> bool:
            if not api_keys:
                return True
            supplied = self.headers.get("X-API-Key") or self.headers.get("Authorization", "").removeprefix("Bearer ")
            return supplied in api_keys

        def within_rate_limit(self) -> bool:
            identity = self.headers.get("X-API-Key") or self.client_address[0]
            now = time.monotonic()
            history = [stamp for stamp in requests.get(identity, []) if now - stamp < 60]
            history.append(now)
            requests[identity] = history
            return len(history) <= rate_limit

        def do_POST(self) -> None:
            if self.path not in {"/v1/compile", "/v2/compile"}:
                self.send_error(404); return
            if not self.authorized():
                self.respond(401, {"error_code":"UNAUTHORIZED","message":"A valid API key is required."}); return
            if not self.within_rate_limit():
                self.respond(429, {"error_code":"RATE_LIMITED","message":"Rate limit exceeded."}); return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > 1_048_576: raise ValueError("Request body must be between 1 and 1,048,576 bytes.")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body.get("expression"), str): raise ValueError("expression must be a string")
                selected = compiler if self.path == "/v1/compile" else compiler_v3
                version = "v1" if self.path == "/v1/compile" else "v2"
                result = selected.compile(body["expression"], body.get("mode", "strict"))
                self.respond(200 if result["valid"] else 400, {"api_version":version, **result})
            except (KeyError, ValueError, json.JSONDecodeError) as error:
                self.respond(400, {"error_code":"INVALID_REQUEST","message":str(error)})
        def log_message(self, *_: object) -> None: pass
    ThreadingHTTPServer((host, port), Handler).serve_forever()
