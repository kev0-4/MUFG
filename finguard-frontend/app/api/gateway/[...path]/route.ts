import type { NextRequest } from "next/server"

const BASE = process.env.NEXT_PUBLIC_API_GATEWAY_BASE_URL! // e.g., http://localhost:8080

export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
  const target = `${BASE}/${params.path.join("/")}`
  console.log("[v0] Proxying GET request to:", target)

  try {
    const bodyText = await req.text() // may be empty; FastAPI GET can accept body
    const res = await fetch(target, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      body: bodyText || undefined,
    })

    console.log("[v0] Gateway response status:", res.status)
    return new Response(await res.text(), {
      status: res.status,
      headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
    })
  } catch (error) {
    console.error("[v0] Proxy GET error:", error)
    return new Response(JSON.stringify({ error: "Proxy request failed" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) {
  const target = `${BASE}/${params.path.join("/")}`
  console.log("[v0] Proxying POST request to:", target)

  try {
    const bodyText = await req.text()
    const res = await fetch(target, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: bodyText,
    })

    console.log("[v0] Gateway response status:", res.status)
    return new Response(await res.text(), {
      status: res.status,
      headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
    })
  } catch (error) {
    console.error("[v0] Proxy POST error:", error)
    return new Response(JSON.stringify({ error: "Proxy request failed" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}
