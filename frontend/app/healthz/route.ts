import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const API_URL = process.env.API_URL ?? "http://localhost:5000";

/** Aggregate health for monitors (e.g. Uptime Kuma): 200 only if web and api are both up. */
export async function GET() {
  let api: "ok" | "error" = "error";
  try {
    const res = await fetch(`${API_URL}/api/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    if (res.ok) api = "ok";
  } catch {
    // unreachable or timed out
  }
  const ok = api === "ok";
  return NextResponse.json(
    { status: ok ? "ok" : "error", frontend: "ok", backend: api },
    { status: ok ? 200 : 503, headers: { "Cache-Control": "no-store" } },
  );
}
