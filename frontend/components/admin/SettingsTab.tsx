"use client";

import { useEffect, useState, type FormEvent } from "react";
import { api } from "@/lib/api";
import type { JobRun, Settings } from "@/lib/types";

const JOB_LABELS: Record<string, string> = {
  refresh_weather: "Weather refresh",
  refresh_kuma: "Uptime Kuma sync",
};

export default function SettingsTab() {
  const [s, setS] = useState<Settings | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [runs, setRuns] = useState<JobRun[]>([]);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const loadRuns = () => api<JobRun[]>("/admin/jobs").then(setRuns).catch(() => {});
  useEffect(() => {
    api<Settings>("/admin/settings").then(setS).catch((e) => setMsg({ ok: false, text: e.message }));
    loadRuns();
  }, []);

  if (!s) return <div className="muted">Loading…</div>;
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
      setMsg({ ok: true, text: "Saved. A new refresh interval applies after the API restarts." });
    } catch (err) {
      setMsg({ ok: false, text: (err as Error).message });
    }
  }

  async function refresh() {
    try {
      await api("/admin/weather/refresh", { method: "POST" });
      setMsg({ ok: true, text: "Weather refreshed." });
    } catch (err) {
      setMsg({ ok: false, text: (err as Error).message });
    }
    loadRuns();
  }

  return (
    <div className="form-grid">
      <form className="form-grid" onSubmit={save}>
        <h3 className="section-title">Weather (Google Weather API)</h3>
        <div className="field">
          <label htmlFor="s-key">
            API key {s.google_weather_api_key_configured && `(configured, ends with ${s.google_weather_api_key_tail})`}
          </label>
          <input id="s-key" className="input" type="password" autoComplete="off" value={apiKey}
                 placeholder={s.google_weather_api_key_configured ? "Leave empty to keep current key" : "Paste API key"}
                 onChange={(e) => setApiKey(e.target.value)} />
        </div>
        <div className="form-2">
          <div className="field">
            <label htmlFor="s-city">City label</label>
            <input id="s-city" className="input" value={s.weather_city} onChange={(e) => set("weather_city", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-lat">Latitude</label>
            <input id="s-lat" className="input" inputMode="decimal" value={s.weather_lat} onChange={(e) => set("weather_lat", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-lon">Longitude</label>
            <input id="s-lon" className="input" inputMode="decimal" value={s.weather_lon} onChange={(e) => set("weather_lon", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-lang">Language code</label>
            <input id="s-lang" className="input" value={s.weather_language} onChange={(e) => set("weather_language", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="s-min">Refresh every (minutes, min 5)</label>
            <input id="s-min" className="input" type="number" min={5} value={s.weather_refresh_minutes} onChange={(e) => set("weather_refresh_minutes", e.target.value)} />
          </div>
        </div>
        <h3 className="section-title">Uptime Kuma</h3>
        <div className="field">
          <label htmlFor="s-kuma">Public base URL (used for status dot links)</label>
          <input id="s-kuma" className="input" type="url" value={s.kuma_base_url} placeholder="https://kuma.example.com"
                 onChange={(e) => set("kuma_base_url", e.target.value)} />
        </div>
        <div className="toolbar">
          <button type="submit" className="btn btn-primary">Save settings</button>
          <button type="button" className="btn btn-secondary" onClick={refresh}>
            <i className="ph ph-arrows-clockwise" /> Refresh weather now
          </button>
          {msg && <span className={msg.ok ? "ok" : "error"}>{msg.text}</span>}
        </div>
      </form>

      <div>
        <h3 className="section-title">Recent job runs</h3>
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Job</th><th>When</th><th>Status</th><th>Message</th></tr></thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td>{JOB_LABELS[r.job_id] ?? r.job_id}</td>
                  <td className="muted">{new Date(r.started_at).toLocaleString("en-GB")}</td>
                  <td><span className={`tag ${r.status === "ok" ? "tag-accent" : "tag-neutral"}`}>{r.status}</span></td>
                  <td className="muted">{r.message}</td>
                </tr>
              ))}
              {runs.length === 0 && <tr><td colSpan={4} className="muted">No runs yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
