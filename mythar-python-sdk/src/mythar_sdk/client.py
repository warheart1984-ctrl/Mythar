from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class MytharAPIError(RuntimeError):
    def __init__(self, status: int, payload: dict) -> None:
        super().__init__(payload.get("message", f"Mythar API request failed ({status})"))
        self.status, self.payload = status, payload


class MytharClient:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str | None = None, timeout: float = 15) -> None:
        self.base_url, self.api_key, self.timeout = base_url.rstrip("/"), api_key, timeout

    def compile(self, expression: str, mode: str = "strict", api_version: str = "v1") -> dict:
        if api_version not in {"v1", "v2"}: raise ValueError("api_version must be v1 or v2")
        headers = {"Content-Type": "application/json"}
        if self.api_key: headers["X-API-Key"] = self.api_key
        request = Request(f"{self.base_url}/{api_version}/compile", data=json.dumps({"expression": expression, "mode": mode}).encode(), headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read())
        except HTTPError as error:
            raise MytharAPIError(error.code, json.loads(error.read())) from error
