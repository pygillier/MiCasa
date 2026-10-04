"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import type { Category } from "@/lib/types";
import Dialog from "./Dialog";

type Draft = Partial<Category>;

export default function CategoriesTab() {
  const { t } = useI18n();
  const [items, setItems] = useState<Category[]>([]);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(
    () => api<Category[]>("/admin/categories").then(setItems).catch((e) => setError(e.message)),
    [],
  );
  useEffect(() => {
    load();
  }, [load]);

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!draft) return;
    try {
      if (draft.id) await api(`/admin/categories/${draft.id}`, { method: "PUT", body: draft });
      else await api("/admin/categories", { method: "POST", body: draft });
      setDraft(null);
      setError("");
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function remove(c: Category) {
    if (!window.confirm(t("categories.confirmDelete", { name: c.name }))) return;
    await api(`/admin/categories/${c.id}`, { method: "DELETE" }).catch((e) => setError(e.message));
    load();
  }

  async function move(i: number, d: -1 | 1) {
    const next = [...items];
    [next[i], next[i + d]] = [next[i + d], next[i]];
    setItems(next);
    await api("/admin/categories/reorder", { method: "PUT", body: { ids: next.map((c) => c.id) } });
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
                <td>
                  <span className={`tag ${c.is_public ? "tag-accent" : "tag-neutral"}`}>
                    {c.is_public ? t("common.public") : t("common.private")}
                  </span>
                </td>
                <td>
                  <div className="row-actions">
                    <button className="btn btn-icon small" disabled={i === 0} aria-label={t("common.moveUp")} onClick={() => move(i, -1)}><i className="ph ph-arrow-up" /></button>
                    <button className="btn btn-icon small" disabled={i === items.length - 1} aria-label={t("common.moveDown")} onClick={() => move(i, 1)}><i className="ph ph-arrow-down" /></button>
                    <button className="btn btn-icon small" aria-label={t("common.edit")} onClick={() => setDraft(c)}><i className="ph ph-pencil-simple" /></button>
                    <button className="btn btn-icon small" aria-label={t("common.delete")} onClick={() => remove(c)}><i className="ph ph-trash" /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {draft && (
        <Dialog title={draft.id ? t("categories.edit") : t("categories.new")} onClose={() => setDraft(null)}>
          <form className="form-grid" onSubmit={save}>
            <div className="field">
              <label htmlFor="c-name">{t("common.name")}</label>
              <input id="c-name" className="input" required maxLength={100} value={draft.name ?? ""}
                     onChange={(e) => setDraft({ ...draft, name: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="c-note">{t("common.note")}</label>
              <input id="c-note" className="input" maxLength={100} value={draft.note ?? ""}
                     onChange={(e) => setDraft({ ...draft, note: e.target.value })} />
            </div>
            <label className="check">
              <input type="checkbox" checked={!!draft.is_public}
                     onChange={(e) => setDraft({ ...draft, is_public: e.target.checked })} />
              {t("categories.publicCheck")}
            </label>
            <div className="dialog-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setDraft(null)}>{t("common.cancel")}</button>
              <button type="submit" className="btn btn-primary">{t("common.save")}</button>
            </div>
          </form>
        </Dialog>
      )}
    </div>
  );
}
