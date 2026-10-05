"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { MESSAGES, type Locale, type MessageKey } from "@/lib/i18n/messages";

type Vars = Record<string, string | number>;
type Ctx = { locale: Locale; t: (key: MessageKey, vars?: Vars) => string };

const I18nContext = createContext<Ctx | null>(null);

export function I18nProvider({ locale, children }: { locale: Locale; children: ReactNode }) {
  const value = useMemo<Ctx>(() => {
    const dict = MESSAGES[locale];
    return {
      locale,
      t: (key, vars) =>
        dict[key].replace(/\{(\w+)\}/g, (_, k) => String(vars?.[k] ?? `{${k}}`)),
    };
  }, [locale]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
