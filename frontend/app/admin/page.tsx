"use client";

import { hardNavigate } from "@/lib/nav";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import CategoriesTab from "@/components/admin/CategoriesTab";
import JobsTab from "@/components/admin/JobsTab";
import LinksTab from "@/components/admin/LinksTab";
import SettingsTab from "@/components/admin/SettingsTab";
import TransferTab from "@/components/admin/TransferTab";
import { api, logout } from "@/lib/api";
import { useI18n } from "@/components/I18nProvider";
import type { MessageKey } from "@/lib/i18n/messages";

const TABS = [
  { id: "links", label: "admin.tab.links", Panel: LinksTab },
  { id: "categories", label: "admin.tab.categories", Panel: CategoriesTab },
  { id: "transfer", label: "admin.tab.transfer", Panel: TransferTab },
  { id: "settings", label: "admin.tab.settings", Panel: SettingsTab },
  { id: "jobs", label: "admin.tab.jobs", Panel: JobsTab },
] as const satisfies readonly { id: string; label: MessageKey; Panel: () => React.ReactNode }[];
type TabId = (typeof TABS)[number]["id"];

export default function AdminPage() {
  const { t } = useI18n();
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<TabId>("links");
  const [menuOpen, setMenuOpen] = useState(false);
  const headRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const onDown = (e: MouseEvent) => {
      if (!headRef.current?.contains(e.target as Node)) setMenuOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMenuOpen(false);
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [menuOpen]);

  useEffect(() => {
    api<{ authenticated: boolean }>("/me").then((me) => {
      if (me.authenticated) setReady(true);
      else hardNavigate("/api/auth/login?next=admin");
    });
  }, []);

  if (!ready) return <div className="admin muted">{t("admin.checking")}</div>;

  const { Panel } = TABS.find((tb) => tb.id === tab)!;

  return (
    <div className="admin">
      <div className="admin-head" ref={headRef}>
        <h1><Image src="/logo.svg" alt="MiCasa" width={147} height={44} unoptimized priority className="admin-logo logo-light" />
          <Image src="/logo-dark.svg" alt="MiCasa" width={147} height={44} unoptimized priority className="admin-logo logo-dark" /> <span className="sr-only">{t("admin.title")}</span></h1>
        <Link href="/" className="btn btn-ghost admin-link"><i className="ph-bold ph-arrow-left" /> {t("nav.startpage")}</Link>
        <button className="btn btn-ghost admin-link" onClick={logout}><i className="ph-bold ph-sign-out" /> {t("nav.logout")}</button>
        <button
          className="btn btn-ghost btn-icon admin-burger"
          aria-label={t("nav.menu")}
          aria-expanded={menuOpen}
          aria-controls="admin-menu"
          onClick={() => setMenuOpen((o) => !o)}
        >
          <i className={`ph-bold ${menuOpen ? "ph-x" : "ph-list"}`} />
        </button>
        {menuOpen && (
          <nav id="admin-menu" className="topbar-menu">
            <Link href="/"><i className="ph-bold ph-arrow-left" /> {t("nav.startpage")}</Link>
            <button onClick={logout}><i className="ph-bold ph-sign-out" /> {t("nav.logout")}</button>
          </nav>
        )}
      </div>
      <div className="tabs" role="tablist">
        {TABS.map((tb) => (
          <button key={tb.id} role="tab" aria-selected={tab === tb.id} className={`tab tab-${tb.id}`} onClick={() => setTab(tb.id)}>
            {t(tb.label)}
          </button>
        ))}
      </div>
      <Panel />
    </div>
  );
}
