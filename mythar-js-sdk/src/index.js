export class MytharAPIError extends Error {
  constructor(status, payload) { super(payload.message || `Mythar API request failed (${status})`); this.status = status; this.payload = payload; }
}

export class MytharClient {
  constructor({ baseUrl = "http://localhost:8080", apiKey, fetchImpl = fetch } = {}) { this.baseUrl = baseUrl.replace(/\/$/, ""); this.apiKey = apiKey; this.fetch = fetchImpl; }
  async compile(expression, { mode = "strict", apiVersion = "v1" } = {}) {
    if (!["v1", "v2"].includes(apiVersion)) throw new Error("apiVersion must be v1 or v2");
    const response = await this.fetch(`${this.baseUrl}/${apiVersion}/compile`, { method: "POST", headers: { "Content-Type": "application/json", ...(this.apiKey ? { "X-API-Key": this.apiKey } : {}) }, body: JSON.stringify({ expression, mode }) });
    const payload = await response.json();
    if (!response.ok) throw new MytharAPIError(response.status, payload);
    return payload;
  }
}
