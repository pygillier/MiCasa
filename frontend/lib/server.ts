import "server-only";
import { cookies } from "next/headers";
import { DEFAULT_THEME, parseTheme, type ThemeId } from "./themes";
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

export async function getTheme(): Promise<ThemeId> {
  try {
    const res = await fetch(`${API_URL}/api/theme`, { cache: "no-store" });
    if (res.ok) return parseTheme((await res.json()).theme);
  } catch {}
  return DEFAULT_THEME;
}
