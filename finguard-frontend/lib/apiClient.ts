import { encryptRequestBody, decryptResponseBody, type EncryptedPayload } from "./crypto/gatewayCrypto"

const BASE = process.env.NEXT_PUBLIC_API_GATEWAY_BASE_URL! // used only by the proxy route

// Calls go to our Next proxy so the browser has same-origin requests and avoids CORS.
async function proxyFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const url = `/api/gateway${path.startsWith("/") ? "" : "/"}${path}`
  return fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  })
}

// POST helper with encryption
export async function postEncrypted<T = any>(path: string, body: object): Promise<T> {
  const encPayload = await encryptRequestBody(body)
  const res = await proxyFetch(path, { method: "POST", body: JSON.stringify(encPayload) })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  const payload = (await res.json()) as EncryptedPayload
  return decryptResponseBody(payload)
}

// GET helper that allows body (some environments may ignore it; our FastAPI accepts it)
export async function getEncrypted<T = any>(path: string, body?: object): Promise<T> {
  let init: RequestInit = { method: "GET" }
  if (body) {
    const encPayload = await encryptRequestBody(body)
    init = { ...init, body: JSON.stringify(encPayload), headers: { "Content-Type": "application/json" } }
  }
  const res = await proxyFetch(path, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  const payload = (await res.json()) as EncryptedPayload
  return decryptResponseBody(payload)
}

export const api = {
  getPublicKey: async () => (await proxyFetch("/api/public-key")).json(),
  userData: (p: { user_id: string }) => postEncrypted("/api/user-data", p),
  simulate: (p: { user_id: string; simulation_data: any }) => postEncrypted("/api/simulate", p),
  recommend: (p: { user_id: string }) => postEncrypted("/api/recommend", p),
  sentiments: (p: { user_id: string }) => postEncrypted("/api/stock-sentiments", p),
  enhance: (p: { user_id: string; simulation_data: any; ai_prompt: string }) => postEncrypted("/api/enhance", p),
  query: (p: { user_id: string; query: string }) => postEncrypted("/api/query", p),
  stockLatest: (ticker: string, body?: object) => getEncrypted(`/api/stock-latest/${encodeURIComponent(ticker)}`, body),
  stockData: (p: { ticker: string; start_date: string; end_date: string }) => postEncrypted("/api/stock-data", p),
}
