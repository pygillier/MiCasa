"use client";

import { hardNavigate } from "@/lib/nav";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import CategoriesTab from "@/components/admin/CategoriesTab";
import LinksTab from "@/components/admin/LinksTab";
import SettingsTab from "@/components/admin/SettingsTab";
import { api } from "@/lib/api";
import { useI18n } from "@/components/I18nProvider";
import type { MessageKey } from "@/lib/i18n/messages";

const TABS = [
  { id: "links", label: "admin.tab.links" },
  { id: "categories", label: "admin.tab.categories" },
  { id: "settings", label: "admin.tab.settings" },
] as const satisfies readonly { id: string; label: MessageKey }[];
type TabId = (typeof TABS)[number]["id"];

export default function AdminPage() {
  const { t } = useI18n();
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<TabId>("links");

  useEffect(() => {
    fetch("/api/me")
      .then((r) => r.json())
      .then((me) => {
        if (me.authenticated) setReady(true);
        else hardNavigate("/api/auth/login?next=admin");
      });
  }, []);

  async function logout() {
    await api("/auth/logout", { method: "POST" });
    hardNavigate("/");
  }

  if (!ready) return <div className="admin muted">{t("admin.checking")}</div>;

  return (
    <div className="admin">
      <div className="admin-head">
        <h1><Image src="/logo-dark.svg" alt="MiCasa" width={147} height={44} unoptimized priority className="admin-logo" /> <span className="sr-only">{t("admin.title")}</span></h1>
        <Link href="/" className="btn btn-ghost"><i className="ph ph-arrow-left" /> {t("nav.startpage")}</Link>
        <button className="btn btn-ghost" onClick={logout}><i className="ph ph-sign-out" /> {t("nav.logout")}</button>
      </div>
      <div className="tabs" role="tablist">
        {TABS.map((tb) => (
          <button key={tb.id} role="tab" aria-selected={tab === tb.id} className="tab" onClick={() => setTab(tb.id)}>
            {t(tb.label)}
          </button>
        ))}
      </div>
      {tab === "categories" && <CategoriesTab />}
      {tab === "links" && <LinksTab />}
      {tab === "settings" && <SettingsTab />}
    </div>
  );
}
