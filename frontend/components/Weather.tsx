"use client";

import { useEffect, useState } from "react";
import type { WeatherData } from "@/lib/types";
import { api } from "@/lib/api";
import { useI18n } from "./I18nProvider";

const WEATHER_POLL_MS = 10 * 60 * 1000;

function weatherIcon(type: string, isDaytime: boolean): string {
  const t = type.toUpperCase();
  if (t.includes("THUNDER")) return "ph-cloud-lightning";
  if (t.includes("SNOW") || t.includes("HAIL") || t.includes("SLEET") || t.includes("FLURR"))
    return "ph-cloud-snow";
  if (t.includes("RAIN") || t.includes("SHOWER") || t.includes("DRIZZLE")) return "ph-cloud-rain";
  if (t.includes("FOG") || t.includes("HAZE") || t.includes("MIST")) return "ph-cloud-fog";
  if (t.includes("WIND")) return "ph-wind";
  if (t === "CLOUDY") return "ph-cloud";
  if (t.includes("CLOUD")) return isDaytime ? "ph-cloud-sun" : "ph-cloud-moon";
  return isDaytime ? "ph-sun" : "ph-moon";
}

export default function Weather() {
  const { t, locale } = useI18n();
  const num = (n: number | null, digits = 1) =>
    n === null || n === undefined ? "–" : n.toLocaleString(locale, { maximumFractionDigits: digits });
  // undefined = loading, null = unavailable
  const [w, setW] = useState<WeatherData | null | undefined>(undefined);
  const [enabled, setEnabled] = useState(true);
  useEffect(() => {
    let alive = true;
    const load = () =>
      api<{ enabled?: boolean; weather: WeatherData | null }>("/weather")
        .then((d) => {
          if (!alive) return;
          setEnabled(d.enabled !== false);
          setW(d.weather);
        })
        .catch(() => alive && setW((prev) => prev ?? null));
    load();
    const id = setInterval(load, WEATHER_POLL_MS);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  if (!enabled) return null;

  return (
    <div className="weather">
      <div className="weather-head">
        <div className="kicker">{t("weather.title")}</div>
        <div className="weather-city">{w?.city}</div>
      </div>
      {w ? (
        <>
          <div className="weather-body">
            <i className={`ph-light ${weatherIcon(w.condition_type, w.is_daytime)} weather-icon`} />
            <div>
              <div className="weather-temp">{num(w.temp)} °C</div>
              <div className="weather-desc">
                {w.condition} · {t("weather.feels", { temp: num(w.feels_like) })}
              </div>
            </div>
          </div>
          <div className="weather-stats">
            <span>↑ {num(w.high, 0)}°</span>
            <span>↓ {num(w.low, 0)}°</span>
            <span>{t("weather.rain", { pct: num(w.rain_pct, 0) })}</span>
            <span>{num(w.wind_kmh, 0)} km/h</span>
          </div>
        </>
      ) : (
        <div className="weather-empty">{w === undefined ? t("weather.loading") : t("weather.unavailable")}</div>
      )}
    </div>
  );
}
