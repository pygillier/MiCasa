"use client";
import { hardNavigate } from "./nav";

export class ApiError extends Error {}

export async function api<T = unknown>(
  path: string,
  opts: { method?: string; body?: unknown } = {},
): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: opts.method ?? "GET",
    headers: { "Content-Type": "application/json", "X-Requested-With": "micasa" },
    body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
  });
  if (res.status === 401) {
    hardNavigate("/api/auth/login?next=admin");
    throw new ApiError("Unauthorized");
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(data.error ?? res.statusText);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}
