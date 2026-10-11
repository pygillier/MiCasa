"use client";

import { useEffect, useRef, useState } from "react";
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

  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const time = now?.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });

  return (
    <>
    {/* Mobile only (see globals.css): the sidebar's greeting/clock/links move here. */}
    <header className="topbar" ref={menuRef}>
      <div className="topbar-info" suppressHydrationWarning>
        <span className="topbar-greet">{now ? t(greetingKey(now.getHours())) : " "}</span>
        <span className="topbar-time">{time ?? " "}</span>
      </div>
      <button
        className="btn btn-ghost btn-icon"
        aria-label={t("nav.menu")}
        aria-expanded={open}
        aria-controls="topbar-menu"
        onClick={() => setOpen((o) => !o)}
      >
        <i className={`ph-bold ${open ? "ph-x" : "ph-list"}`} />
      </button>
      {open && (
        <nav id="topbar-menu" className="topbar-menu">
          {authenticated ? (
            <>
              <a href="/admin">
                <i className="ph-bold ph-gear" /> {t("nav.admin")}
              </a>
              <button onClick={logout}>
                <i className="ph-bold ph-sign-out" /> {t("nav.logout")}
              </button>
            </>
          ) : (
            <a href="/api/auth/login">
              <i className="ph-bold ph-sign-in" /> {t("nav.login")}
            </a>
          )}
        </nav>
      )}
    </header>
    <aside className="side">
      <div className="side-intro">
        <div className="kicker" suppressHydrationWarning>
          {now?.toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long" }) ?? " "}
        </div>
        <h1 className="greeting">{now ? t(greetingKey(now.getHours())) : " "}</h1>
      </div>
      <div className="clock-row">
        <div className="clock">
          {time}
        </div>
        <div className="tz">{tz}</div>
      </div>
      <Weather />
      <div className="side-foot">
        {authenticated ? (
          <>
            <a href="/admin" className="btn btn-ghost">
              <i className="ph-bold ph-gear" /> {t("nav.admin")}
            </a>
            <button className="btn btn-ghost" onClick={logout}>
              <i className="ph-bold ph-sign-out" /> {t("nav.logout")}
            </button>
          </>
        ) : (
          <a href="/api/auth/login" className="btn btn-ghost">
            <i className="ph-bold ph-sign-in" /> {t("nav.login")}
          </a>
        )}
      </div>
    </aside>
    </>
  );
}
