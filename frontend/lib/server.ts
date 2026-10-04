import "server-only";
import { cookies } from "next/headers";
import type { Startpage } from "./types";

const API_URL = process.env.API_URL ?? "http://localhost:5000";

export async function getStartpage(): Promise<Startpage> {
  const jar = await cookies();
  const res = await fetch(`${API_URL}/api/startpage`, {
    cache: "no-store",
    headers: { cookie: jar.toString() },
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
