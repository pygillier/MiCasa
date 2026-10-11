"use client";

import { useRef, useState, type ChangeEvent } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import { Notice, type Msg } from "./shared";

interface ImportResult {
  categories_created: number;
  links_created: number;
  skipped: number;
}

export default function TransferTab() {
  const { t } = useI18n();
  const fileRef = useRef<HTMLInputElement>(null);
  const [msg, setMsg] = useState<Msg | null>(null);

  async function onFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const r = await api<ImportResult>("/admin/import", {
        method: "POST", body: file, contentType: "text/x-opml",
      });
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
        <Notice msg={msg} />
      </div>
    </div>
  );
}
