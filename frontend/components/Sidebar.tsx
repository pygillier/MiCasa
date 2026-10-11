"use client";

import { useEffect, useState } from "react";
import { logout } from "@/lib/api";
import { useI18n } from "./I18nProvider";
import Weather from "./Weather";

function greetingKey(h: number) {
  if (h < 5) return "greeting.night";
  if (h < 12) return "greeting.morning";
  if (h < 18) return "greeting.afternoon";
  return "greeting.evening";
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

export default function Sidebar({ authenticated }: { authenticated: boolean }) {
  const { t, locale } = useI18n();
  const now = useNow();
  const tz = now
    ? new Intl.DateTimeFormat(locale, { timeZoneName: "short" })
        .formatToParts(now)
        .find((p) => p.type === "timeZoneName")?.value
    : "";

  return (
    <aside className="side">
      <div>
        <div className="kicker" suppressHydrationWarning>
          {now?.toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long" }) ?? " "}
        </div>
        <h1 className="greeting">{now ? t(greetingKey(now.getHours())) : " "}</h1>
      </div>
      <div className="clock-row">
        <div className="clock">
          {now?.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
        </div>
        <div className="tz">{tz}</div>
      </div>
      <Weather />
      <div className="side-foot">
        {authenticated ? (
          <>
            <a href="/admin" className="btn btn-ghost">
              <i className="ph ph-gear" /> {t("nav.admin")}
            </a>
            <button className="btn btn-ghost" onClick={logout}>
              <i className="ph ph-sign-out" /> {t("nav.logout")}
            </button>
          </>
        ) : (
          <a href="/api/auth/login" className="btn btn-ghost">
            <i className="ph ph-sign-in" /> {t("nav.login")}
          </a>
        )}
      </div>
    </aside>
  );
}
