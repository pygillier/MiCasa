"use client";

/** Full-page navigation (auth redirects, or reloading server-rendered data). */
export function hardNavigate(url: string) {
  window.location.href = url;
}
