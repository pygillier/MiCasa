"use client";

import { useRef, useState, type ChangeEvent } from "react";
import { useI18n } from "@/components/I18nProvider";

interface ImportResult {
  categories_created: number;
  links_created: number;
  skipped: number;
}

export default function TransferTab() {
  const { t } = useI18n();
  const fileRef = useRef<HTMLInputElement>(null);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  async function onFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const res = await fetch("/api/admin/import", {
        method: "POST",
        headers: { "Content-Type": "text/x-opml", "X-Requested-With": "micasa" },
        body: file,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error ?? res.statusText);
      const r = data as ImportResult;
      setMsg({
        ok: true,
        text: t("transfer.result", { cats: r.categories_created, links: r.links_created, skipped: r.skipped }),
      });
    } catch (err) {
      setMsg({ ok: false, text: (err as Error).message });
    }
  }

  return (
    <div className="form-grid">
      <h3 className="section-title">{t("transfer.exportTitle")}</h3>
      <p className="muted">{t("transfer.exportHelp")}</p>
      <div className="toolbar">
        <a className="btn btn-secondary" href="/api/admin/export.opml" download="micasa.opml">
          <i className="ph ph-download-simple" /> {t("transfer.exportBtn")}
        </a>
      </div>

      <h3 className="section-title">{t("transfer.importTitle")}</h3>
      <p className="muted">{t("transfer.importHelp")}</p>
      <div className="toolbar">
        <input ref={fileRef} type="file" accept=".opml,.xml,text/xml,text/x-opml" hidden onChange={onFile} />
        <button type="button" className="btn btn-secondary" onClick={() => fileRef.current?.click()}>
          <i className="ph ph-upload-simple" /> {t("transfer.importBtn")}
        </button>
        {msg && <span className={msg.ok ? "ok" : "error"}>{msg.text}</span>}
      </div>
    </div>
  );
}
