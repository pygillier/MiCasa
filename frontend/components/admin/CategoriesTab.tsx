"use client";

import { useCallback, useState } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import type { Category } from "@/lib/types";
import Dialog from "./Dialog";
import { RowActions, TextField, VisibilityTag, swap } from "./shared";
import { useAdminCrud } from "./useAdminCrud";

export default function CategoriesTab() {
  const { t } = useI18n();
  const [items, setItems] = useState<Category[]>([]);
  const load = useCallback(() => api<Category[]>("/admin/categories").then(setItems), []);
  const { draft, setDraft, error, save, remove, reorder } = useAdminCrud<Partial<Category>>("categories", load);

  function move(i: number, d: -1 | 1) {
    const next = swap(items, i, d);
    setItems(next);
    reorder(next.map((c) => c.id));
  }

  return (
    <div className="form-grid">
      <div className="toolbar">
        <span className="spacer muted">{t("categories.count", { n: items.length })}</span>
        <button className="btn btn-primary" onClick={() => setDraft({ is_public: false })}>
          <i className="ph ph-plus" /> {t("categories.new")}
        </button>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr><th>{t("common.name")}</th><th>{t("common.note")}</th><th>{t("common.visibility")}</th><th /></tr>
          </thead>
          <tbody>
            {items.map((c, i) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td className="muted">{c.note}</td>
                <td><VisibilityTag isPublic={c.is_public} /></td>
                <td>
                  <RowActions index={i} count={items.length} onMove={(d) => move(i, d)}
                              onEdit={() => setDraft(c)}
                              onDelete={() => remove(c.id, "categories.confirmDelete", { name: c.name })} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {draft && (
        <Dialog title={draft.id ? t("categories.edit") : t("categories.new")}
                onClose={() => setDraft(null)} onSubmit={save}>
          <TextField id="c-name" label={t("common.name")} required maxLength={100}
                     value={draft.name ?? ""} onChange={(name) => setDraft({ ...draft, name })} />
          <TextField id="c-note" label={t("common.note")} maxLength={100}
                     value={draft.note ?? ""} onChange={(note) => setDraft({ ...draft, note })} />
          <label className="check">
            <input type="checkbox" checked={!!draft.is_public}
                   onChange={(e) => setDraft({ ...draft, is_public: e.target.checked })} />
            {t("categories.publicCheck")}
          </label>
        </Dialog>
      )}
    </div>
  );
}
