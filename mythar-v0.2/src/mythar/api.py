from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .core import MytharCompiler, REGISTRY_DIR
from .isf import to_isf
from .semantic_input import normalize_source
from .transduce.english import translate_isf
from .transduce.mandarin import translate_isf as translate_to_mandarin


def serve(port: int, host: str = "127.0.0.1") -> None:
    compiler = MytharCompiler()
    compiler_v3 = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json")
    api_keys = {key.strip() for key in os.getenv("MYTHAR_API_KEYS", "").split(",") if key.strip()}
    rate_limit = int(os.getenv("MYTHAR_RATE_LIMIT", "60"))
    requests: dict[str, list[float]] = {}

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status: int, payload: dict, version: str = "v1") -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("X-Mythar-API-Version", version)
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

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
            request_url = urlparse(self.path)
            if request_url.path not in {"/v1/compile", "/v2/compile"}:
                self.send_error(404); return
            if not self.authorized():
                self.respond(401, {"error_code":"UNAUTHORIZED","message":"A valid API key is required."}); return
            if not self.within_rate_limit():
                self.respond(429, {"error_code":"RATE_LIMITED","message":"Rate limit exceeded."}); return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > 1_048_576: raise ValueError("Request body must be between 1 and 1,048,576 bytes.")
                body = json.loads(self.rfile.read(size))
                expression = body.get("expression", body.get("source"))
                if not isinstance(expression, str): raise ValueError("expression or source must be a string")
                selected = compiler if request_url.path == "/v1/compile" else compiler_v3
                version = "v1" if request_url.path == "/v1/compile" else "v2"
                output_format = parse_qs(request_url.query).get("format", [body.get("format", "ast")])[0]
                if output_format not in {"ast", "isf", "english", "mandarin"}: raise ValueError("format must be ast, isf, english, or mandarin")
                if output_format in {"isf", "english", "mandarin"} and version != "v2": raise ValueError("ISF and translation output are available only from /v2/compile")
                source_language = body.get("source_language", "mythar")
                if version == "v1" and source_language != "mythar": raise ValueError("source_language is available only from /v2/compile")
                result = selected.compile(normalize_source(expression, source_language), body.get("mode", "strict"))
                payload = {"api_version":version, **result}
                if output_format in {"isf", "english", "mandarin"} and result["valid"]:
                    isf = to_isf(result, source_language)
                    payload = {"api_version":version, **result, "isf": isf}
                    if output_format == "english":
                        payload["translation"] = {"language": "en", "text": translate_isf(isf)}
                    if output_format == "mandarin":
                        payload["translation"] = {"language": "zh", "text": translate_to_mandarin(isf)}
                self.respond(200 if result["valid"] else 400, payload, version)
            except (KeyError, ValueError, json.JSONDecodeError) as error:
                self.respond(400, {"error_code":"INVALID_REQUEST","message":str(error)})
        def log_message(self, *_: object) -> None: pass
    ThreadingHTTPServer((host, port), Handler).serve_forever()
