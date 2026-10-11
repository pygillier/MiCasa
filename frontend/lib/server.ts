import "server-only";
import { cookies } from "next/headers";
import { DEFAULT_THEME, DEFAULT_THEME_DAY, parseTheme, type ThemeId } from "./themes";
import type { Startpage } from "./types";

const DEFAULT_TITLE = "MiCasa";
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

export async function getSiteTitle(): Promise<string> {
  try {
    const res = await fetch(`${API_URL}/api/site`, { cache: "no-store" });
    if (res.ok) return (await res.json()).title || DEFAULT_TITLE;
  } catch {}
  return DEFAULT_TITLE;
}

export async function getThemes(): Promise<{ night: ThemeId; day: ThemeId }> {
  try {
    const res = await fetch(`${API_URL}/api/theme`, { cache: "no-store" });
    if (res.ok) {
      const body = await res.json();
      return { night: parseTheme(body.theme), day: parseTheme(body.theme_day) };
    }
  } catch {}
  return { night: DEFAULT_THEME, day: DEFAULT_THEME_DAY };
}
