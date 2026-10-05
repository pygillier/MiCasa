export const THEMES = [
  { id: "nocturne", name: "Nocturne" },
  { id: "home", name: "Home" },
] as const;
export type ThemeId = (typeof THEMES)[number]["id"];
export const DEFAULT_THEME: ThemeId = "nocturne";

export function parseTheme(value: string | undefined | null): ThemeId {
  return THEMES.find((t) => t.id === value)?.id ?? DEFAULT_THEME;
}
