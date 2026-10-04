"use client";

import { hardNavigate } from "@/lib/nav";
import { useEffect, useState } from "react";
import type { WeatherData } from "@/lib/types";
import { api } from "@/lib/api";
import { weatherIcon } from "./weather";

const WEATHER_POLL_MS = 10 * 60 * 1000;
const num = (n: number | null, digits = 1) =>
  n === null || n === undefined ? "–" : n.toLocaleString("fr-FR", { maximumFractionDigits: digits });

function greeting(h: number) {
  if (h < 5) return "Good night";
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function useNow() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    const tick = () => setNow(new Date());
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

function Weather() {
  const [w, setW] = useState<WeatherData | null | undefined>(undefined);
  useEffect(() => {
    let alive = true;
    const load = () =>
      fetch("/api/weather")
        .then((r) => r.json())
        .then((d) => alive && setW(d.weather))
        .catch(() => alive && setW((prev) => prev ?? null));
    load();
    const id = setInterval(load, WEATHER_POLL_MS);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="weather">
      <div className="weather-head">
        <div className="kicker">Weather</div>
        <div className="weather-city">{w?.city}</div>
      </div>
      {w ? (
        <>
          <div className="weather-body">
            <i className={`ph-light ${weatherIcon(w.condition_type, w.is_daytime)} weather-icon`} />
            <div>
              <div className="weather-temp">{num(w.temp)} °C</div>
              <div className="weather-desc">
                {w.condition} · feels {num(w.feels_like)} °C
              </div>
            </div>
          </div>
          <div className="weather-stats">
            <span>↑ {num(w.high, 0)}°</span>
            <span>↓ {num(w.low, 0)}°</span>
            <span>{num(w.rain_pct, 0)} % rain</span>
            <span>{num(w.wind_kmh, 0)} km/h</span>
          </div>
        </>
      ) : (
        <div className="weather-empty">{w === undefined ? "Loading…" : "Weather unavailable"}</div>
      )}
    </div>
  );
}

export default function Sidebar({ authenticated }: { authenticated: boolean }) {
  const now = useNow();
  const tz = now
    ? new Intl.DateTimeFormat("en", { timeZoneName: "short" })
        .formatToParts(now)
        .find((p) => p.type === "timeZoneName")?.value
    : "";

  async function logout() {
    await api("/auth/logout", { method: "POST" });
    hardNavigate("/");
  }

  return (
    <aside className="side">
      <div>
        <div className="kicker" suppressHydrationWarning>
          {now?.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" }) ?? " "}
        </div>
        <h1 className="greeting">{now ? greeting(now.getHours()) : " "}</h1>
      </div>
      <div className="clock-row">
        <div className="clock">
          {now?.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}
        </div>
        <div className="tz">{tz}</div>
      </div>
      <Weather />
      <div className="side-foot">
        {authenticated ? (
          <>
            <a href="/admin" className="btn btn-ghost">
              <i className="ph ph-gear" /> Admin
            </a>
            <button className="btn btn-ghost" onClick={logout}>
              <i className="ph ph-sign-out" /> Log out
            </button>
          </>
        ) : (
          <a href="/api/auth/login" className="btn btn-ghost">
            <i className="ph ph-sign-in" /> Log in
          </a>
        )}
      </div>
    </aside>
  );
}
