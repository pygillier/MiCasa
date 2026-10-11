"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useI18n } from "@/components/I18nProvider";
import { THEMES, applyThemes, parseTheme } from "@/lib/themes";
import { api } from "@/lib/api";
import type { Settings } from "@/lib/types";
import { Field, Notice, TextField, type Msg } from "./shared";

export default function SettingsTab() {
  const { t } = useI18n();
  const [s, setS] = useState<Settings | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [msg, setMsg] = useState<Msg | null>(null);

  useEffect(() => {
    api<Settings>("/admin/settings").then(setS).catch((e) => setMsg({ ok: false, text: e.message }));
  }, []);

  if (!s) return <div className="muted">{t("common.loading")}</div>;
  const set = (k: keyof Settings) => (v: string) => setS({ ...s, [k]: v });

  async function run(action: () => Promise<string>) {
    try {
      setMsg({ ok: true, text: await action() });
    } catch (err) {
      setMsg({ ok: false, text: (err as Error).message });
    }
  }

  const save = (e: FormEvent) => {
    e.preventDefault();
    return run(async () => {
      const body = {
        weather_city: s.weather_city,
        weather_lat: s.weather_lat,
        weather_lon: s.weather_lon,
        weather_language: s.weather_language,
        weather_refresh_minutes: s.weather_refresh_minutes,
        kuma_base_url: s.kuma_base_url,
        site_title: s.site_title,
        theme: s.theme,
        theme_day: s.theme_day,
        google_weather_api_key: apiKey,
      };
      const saved = await api<Settings>("/admin/settings", { method: "PUT", body });
      setS(saved);
      applyThemes(saved.theme, saved.theme_day);
      setApiKey("");
      return t("settings.saved");
    });
  };

  const refresh = () =>
    run(async () => {
      await api("/admin/weather/refresh", { method: "POST" });
      return t("settings.refreshed");
    });

  return (
    <div className="form-grid">
      <form className="form-grid" onSubmit={save}>
        <h3 className="section-title">{t("settings.appearanceTitle")}</h3>
        <TextField id="s-title" label={t("settings.siteTitle")} placeholder="MiCasa"
                   value={s.site_title} onChange={set("site_title")} />
        <Field id="s-theme" label={t("settings.themeNight")}>
          <select id="s-theme" className="input" value={parseTheme(s.theme)}
                  onChange={(e) => {
                    set("theme")(e.target.value);
                    applyThemes(e.target.value, s.theme_day);
                  }}>
            {THEMES.map((th) => <option key={th.id} value={th.id}>{th.name}</option>)}
          </select>
        </Field>
        <Field id="s-theme-day" label={t("settings.themeDay")}>
          <select id="s-theme-day" className="input" value={parseTheme(s.theme_day)}
                  onChange={(e) => {
                    set("theme_day")(e.target.value);
                    applyThemes(s.theme, e.target.value);
                  }}>
            {THEMES.map((th) => <option key={th.id} value={th.id}>{th.name}</option>)}
          </select>
        </Field>
        <h3 className="section-title">{t("settings.weatherTitle")}</h3>
        <TextField id="s-key" type="password" autoComplete="off" value={apiKey} onChange={setApiKey}
                   label={<>{t("settings.apiKey")} {s.google_weather_api_key_configured && t("settings.apiKeyConfigured", { tail: s.google_weather_api_key_tail })}</>}
                   placeholder={s.google_weather_api_key_configured ? t("settings.apiKeyKeep") : t("settings.apiKeyPaste")} />
        <div className="form-2">
          <TextField id="s-city" label={t("settings.city")} value={s.weather_city} onChange={set("weather_city")} />
          <TextField id="s-lat" label={t("settings.lat")} inputMode="decimal" value={s.weather_lat} onChange={set("weather_lat")} />
          <TextField id="s-lon" label={t("settings.lon")} inputMode="decimal" value={s.weather_lon} onChange={set("weather_lon")} />
          <TextField id="s-lang" label={t("settings.lang")} value={s.weather_language} onChange={set("weather_language")} />
          <TextField id="s-min" label={t("settings.refreshEvery")} type="number" min={5}
                     value={s.weather_refresh_minutes} onChange={set("weather_refresh_minutes")} />
        </div>
        <h3 className="section-title">{t("settings.kumaTitle")}</h3>
        <TextField id="s-kuma" label={t("settings.kumaUrl")} type="url" placeholder="https://kuma.example.com"
                   value={s.kuma_base_url} onChange={set("kuma_base_url")} />
        <div className="toolbar">
          <button type="submit" className="btn btn-primary">{t("settings.save")}</button>
          <button type="button" className="btn btn-secondary" onClick={refresh}>
            <i className="ph-bold ph-arrows-clockwise" /> {t("settings.refreshNow")}
          </button>
          <Notice msg={msg} />
        </div>
      </form>
    </div>
  );
}
