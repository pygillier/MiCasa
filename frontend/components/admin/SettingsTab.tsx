"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import type { JobRun, Settings } from "@/lib/types";
import type { MessageKey } from "@/lib/i18n/messages";

const JOB_IDS = ["refresh_weather", "refresh_kuma"];

export default function SettingsTab() {
  const { t, locale } = useI18n();
  const [s, setS] = useState<Settings | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [runs, setRuns] = useState<JobRun[]>([]);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const loadRuns = () => api<JobRun[]>("/admin/jobs").then(setRuns).catch(() => {});
  useEffect(() => {
    api<Settings>("/admin/settings").then(setS).catch((e) => setMsg({ ok: false, text: e.message }));
    loadRuns();
  }, []);

  if (!s) return <div className="muted">{t("common.loading")}</div>;
  const set = (k: keyof Settings, v: string) => setS({ ...s, [k]: v });

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!s) return;
    try {
      const body = {
        weather_city: s.weather_city,
        weather_lat: s.weather_lat,
        weather_lon: s.weather_lon,
        weather_language: s.weather_language,
        weather_refresh_minutes: s.weather_refresh_minutes,
        kuma_base_url: s.kuma_base_url,
        google_weather_api_key: apiKey,
      };
      setS(await api<Settings>("/admin/settings", { method: "PUT", body }));
      setApiKey("");
      setMsg({ ok: true, text: t("settings.saved") });
    } catch (err) {
      setMsg({ ok: false, text: (err as Error).message });
    }
  }

  async function refresh() {
    try {
      await api("/admin/weather/refresh", { method: "POST" });
      setMsg({ ok: true, text: t("settings.refreshed") });
    } catch (err) {
      setMsg({ ok: false, text: (err as Error).message });
    }
    loadRuns();
  }

  return (
    <div className="form-grid">
      <form className="form-grid" onSubmit={save}>
        <h3 className="section-title">{t("settings.weatherTitle")}</h3>
        <div className="field">
          <label htmlFor="s-key">
            {t("settings.apiKey")} {s.google_weather_api_key_configured && t("settings.apiKeyConfigured", { tail: s.google_weather_api_key_tail })}
          </label>
          <input id="s-key" className="input" type="password" autoComplete="off" value={apiKey}
                 placeholder={s.google_weather_api_key_configured ? t("settings.apiKeyKeep") : t("settings.apiKeyPaste")}
                 onChange={(e) => setApiKey(e.target.value)} />
        </div>
        <div className="form-2">
          <div className="field">
            <label htmlFor="s-city">{t("settings.city")}</label>
            <input id="s-city" className="input" value={s.weather_city} onChange={(e) => set("weather_city", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-lat">{t("settings.lat")}</label>
            <input id="s-lat" className="input" inputMode="decimal" value={s.weather_lat} onChange={(e) => set("weather_lat", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-lon">{t("settings.lon")}</label>
            <input id="s-lon" className="input" inputMode="decimal" value={s.weather_lon} onChange={(e) => set("weather_lon", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-lang">{t("settings.lang")}</label>
            <input id="s-lang" className="input" value={s.weather_language} onChange={(e) => set("weather_language", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-min">{t("settings.refreshEvery")}</label>
            <input id="s-min" className="input" type="number" min={5} value={s.weather_refresh_minutes} onChange={(e) => set("weather_refresh_minutes", e.target.value)} />
          </div>
        </div>
        <h3 className="section-title">{t("settings.kumaTitle")}</h3>
        <div className="field">
          <label htmlFor="s-kuma">{t("settings.kumaUrl")}</label>
          <input id="s-kuma" className="input" type="url" value={s.kuma_base_url} placeholder="https://kuma.example.com"
                 onChange={(e) => set("kuma_base_url", e.target.value)} />
        </div>
        <div className="toolbar">
          <button type="submit" className="btn btn-primary">{t("settings.save")}</button>
          <button type="button" className="btn btn-secondary" onClick={refresh}>
            <i className="ph ph-arrows-clockwise" /> {t("settings.refreshNow")}
          </button>
          {msg && <span className={msg.ok ? "ok" : "error"}>{msg.text}</span>}
        </div>
      </form>

      <div>
        <h3 className="section-title">{t("settings.runs")}</h3>
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>{t("settings.job")}</th><th>{t("settings.when")}</th><th>{t("settings.status")}</th><th>{t("settings.message")}</th></tr></thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td>{JOB_IDS.includes(r.job_id) ? t(`settings.job.${r.job_id}` as MessageKey) : r.job_id}</td>
                  <td className="muted">{new Date(r.started_at).toLocaleString(locale)}</td>
                  <td><span className={`tag ${r.status === "ok" ? "tag-accent" : "tag-neutral"}`}>{r.status}</span></td>
                  <td className="muted">{r.message}</td>
                </tr>
              ))}
              {runs.length === 0 && <tr><td colSpan={4} className="muted">{t("settings.noRuns")}</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
