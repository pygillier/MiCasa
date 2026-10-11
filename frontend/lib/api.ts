"use client";
import { hardNavigate } from "./nav";

export class ApiError extends Error {}

/** JSON request to the Flask API; a `Blob` body is sent as-is with `contentType`. */
export async function api<T = unknown>(
  path: string,
  opts: { method?: string; body?: unknown; contentType?: string } = {},
): Promise<T> {
  const { body } = opts;
  const res = await fetch(`/api${path}`, {
    method: opts.method ?? "GET",
    headers: { "Content-Type": opts.contentType ?? "application/json", "X-Requested-With": "micasa" },
    body: body === undefined ? undefined : body instanceof Blob ? body : JSON.stringify(body),
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

export async function logout() {
  await api("/auth/logout", { method: "POST" });
  hardNavigate("/");
}
