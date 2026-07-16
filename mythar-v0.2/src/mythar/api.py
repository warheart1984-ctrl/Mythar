from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .core import MytharCompiler


def serve(port: int) -> None:
    compiler = MytharCompiler()
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != "/v1/compile":
                self.send_error(404); return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(size))
                result = compiler.compile(body["expression"], body.get("mode", "strict"))
                self.send_response(200 if result["valid"] else 400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except (KeyError, ValueError, json.JSONDecodeError) as error:
                self.send_response(400); self.send_header("Content-Type", "application/json"); self.end_headers()
                self.wfile.write(json.dumps({"error_code":"INVALID_REQUEST","message":str(error)}).encode())
        def log_message(self, *_: object) -> None: pass
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
