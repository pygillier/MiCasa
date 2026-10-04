"use client";

import { hardNavigate } from "@/lib/nav";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import CategoriesTab from "@/components/admin/CategoriesTab";
import LinksTab from "@/components/admin/LinksTab";
import SettingsTab from "@/components/admin/SettingsTab";
import { api } from "@/lib/api";

const TABS = [
  { id: "categories", label: "Categories" },
  { id: "links", label: "Links" },
  { id: "settings", label: "Settings" },
] as const;
type TabId = (typeof TABS)[number]["id"];

export default function AdminPage() {
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

  if (!ready) return <div className="admin muted">Checking session…</div>;

  return (
    <div className="admin">
      <div className="admin-head">
        <h1><Image src="/logo-dark.svg" alt="MiCasa" width={147} height={44} unoptimized priority className="admin-logo" /> <span className="sr-only">Admin</span></h1>
        <Link href="/" className="btn btn-ghost"><i className="ph ph-arrow-left" /> Startpage</Link>
        <button className="btn btn-ghost" onClick={logout}><i className="ph ph-sign-out" /> Log out</button>
      </div>
      <div className="tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id} className="tab" onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>
      {tab === "categories" && <CategoriesTab />}
      {tab === "links" && <LinksTab />}
      {tab === "settings" && <SettingsTab />}
    </div>
  );
}
