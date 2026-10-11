export const THEMES = [
  { id: "nocturne", name: "Nocturne" },
  { id: "home", name: "Home" },
  { id: "home-day", name: "Home (daylight)" },
] as const;
export type ThemeId = (typeof THEMES)[number]["id"];
export const DEFAULT_THEME: ThemeId = "nocturne";
export const DEFAULT_THEME_DAY: ThemeId = "home-day";

export function parseTheme(value: string | undefined | null): ThemeId {
  return THEMES.find((t) => t.id === value)?.id ?? DEFAULT_THEME;
}

/** Sets the night / day themes on <html>; the inline script in layout.tsx picks one from the OS preference. */
export function applyThemes(night: string, day: string) {
  const el = document.documentElement;
  el.dataset.themeNight = parseTheme(night);
  el.dataset.themeDay = parseTheme(day);
  el.dataset.theme = matchMedia("(prefers-color-scheme: light)").matches ? el.dataset.themeDay : el.dataset.themeNight;
}

/** Runs before first paint and on every OS scheme change; reads the data attributes set by applyThemes. */
export const THEME_SCRIPT = `(function(){var d=document.documentElement,m=matchMedia("(prefers-color-scheme: light)");function a(){d.dataset.theme=m.matches?d.dataset.themeDay:d.dataset.themeNight}a();m.addEventListener("change",a)})()`;
