"use client";

import { useCallback, useEffect, useState } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import type { AdminLink, Category, Monitor } from "@/lib/types";
import Dialog from "./Dialog";
import { Field, RowActions, TextField, VisibilityTag, swap } from "./shared";
import { useAdminCrud } from "./useAdminCrud";

export default function LinksTab() {
  const { t } = useI18n();
  const [cats, setCats] = useState<Category[]>([]);
  const [links, setLinks] = useState<AdminLink[]>([]);
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [monitorError, setMonitorError] = useState("");

  const load = useCallback(
    () =>
      Promise.all([api<Category[]>("/admin/categories"), api<AdminLink[]>("/admin/links")]).then(
        ([c, l]) => {
          setCats(c);
          setLinks(l);
        },
      ),
    [],
  );
  const { draft, setDraft, error, save, remove, reorder } = useAdminCrud<Partial<AdminLink>>("links", load);

  useEffect(() => {
    api<Monitor[]>("/admin/kuma/monitors")
      .then(setMonitors)
      .catch((e) => setMonitorError(e.message));
  }, []);

  function move(catId: number, i: number, d: -1 | 1) {
    const group = swap(links.filter((l) => l.category_id === catId), i, d);
    setLinks([...links.filter((l) => l.category_id !== catId), ...group]);
    reorder(group.map((l) => l.id));
  }

  const monitorName = (id: number) => monitors.find((m) => m.id === id)?.name ?? `#${id}`;

  return (
    <div className="form-grid">
      <div className="toolbar">
        <span className="spacer muted">{t("links.count", { n: links.length })}</span>
        <button className="btn btn-primary" disabled={cats.length === 0}
                onClick={() => setDraft({
                  category_id: cats[0]?.id, icon: "ph-link", is_public: false, kuma_monitor_id: null,
                })}>
          <i className="ph ph-plus" /> {t("links.new")}
        </button>
      </div>
      {cats.length === 0 && <div className="muted">{t("links.createCategoryFirst")}</div>}
      {error && <div className="error">{error}</div>}

      {cats.map((c) => {
        const group = links.filter((l) => l.category_id === c.id);
        return (
          <div key={c.id}>
            <h3 className="section-title">{c.name}</h3>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr><th /><th>{t("links.label")}</th><th>{t("links.url")}</th><th>{t("links.monitor")}</th><th>{t("common.visibility")}</th><th /></tr>
                </thead>
                <tbody>
                  {group.map((l, i) => (
                    <tr key={l.id}>
                      <td><i className={`ph ${l.icon}`} /></td>
                      <td>{l.label}</td>
                      <td className="muted">{l.url}</td>
                      <td>
                        {l.kuma_monitor_id !== null && (
                          <span style={{ display: "inline-flex", gap: "var(--space-2)", alignItems: "center" }}>
                            <span className={`tag tag-status-${l.monitor_status ?? "pending"}`}>
                              {t(`status.${l.monitor_status ?? "pending"}` as "status.up")}
                            </span>
                            <span className="muted">{monitorName(l.kuma_monitor_id)}</span>
                          </span>
                        )}
                      </td>
                      <td><VisibilityTag isPublic={l.is_public} /></td>
                      <td>
                        <RowActions index={i} count={group.length} onMove={(d) => move(c.id, i, d)}
                                    onEdit={() => setDraft(l)}
                                    onDelete={() => remove(l.id, "links.confirmDelete", { label: l.label })} />
                      </td>
                    </tr>
                  ))}
                  {group.length === 0 && (
                    <tr><td colSpan={6} className="muted">{t("links.none")}</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}

      {draft && (
        <Dialog title={draft.id ? t("links.edit") : t("links.new")}
                onClose={() => setDraft(null)} onSubmit={save}>
          <div className="form-2">
            <TextField id="l-label" label={t("links.label")} required maxLength={100}
                       value={draft.label ?? ""} onChange={(label) => setDraft({ ...draft, label })} />
            <Field id="l-cat" label={t("links.category")}>
              <select id="l-cat" className="input" value={draft.category_id}
                      onChange={(e) => setDraft({ ...draft, category_id: Number(e.target.value) })}>
                {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </Field>
          </div>
          <TextField id="l-url" label={t("links.url")} type="url" required placeholder="https://"
                     value={draft.url ?? ""} onChange={(url) => setDraft({ ...draft, url })} />
          <div className="form-2">
            <Field id="l-icon" label={t("links.iconLabel", { link: "Phosphor" })}>
              <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "center" }}>
                <i className={`ph ${draft.icon}`} style={{ fontSize: "1.25rem" }} />
                <input id="l-icon" className="input" pattern="ph-[a-z0-9-]+" placeholder="ph-house-line"
                       value={draft.icon ?? ""} onChange={(e) => setDraft({ ...draft, icon: e.target.value })} />
              </div>
            </Field>
            <TextField id="l-host" label={t("links.hostLabel")} maxLength={100}
                       value={draft.host ?? ""} onChange={(host) => setDraft({ ...draft, host })} />
          </div>
          <Field id="l-mon" label={t("links.kumaMonitor")}>
            <select id="l-mon" className="input" value={draft.kuma_monitor_id ?? ""}
                    onChange={(e) => setDraft({ ...draft, kuma_monitor_id: e.target.value === "" ? null : Number(e.target.value) })}>
              <option value="">{t("links.none.option")}</option>
              {draft.kuma_monitor_id != null && !monitors.some((m) => m.id === draft.kuma_monitor_id) && (
                <option value={draft.kuma_monitor_id}>#{draft.kuma_monitor_id}</option>
              )}
              {monitors.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
            {monitorError && <div className="error">{monitorError}</div>}
          </Field>
          <label className="check">
            <input type="checkbox" checked={!!draft.is_public}
                   onChange={(e) => setDraft({ ...draft, is_public: e.target.checked })} />
            {t("links.publicCheck")}
          </label>
        </Dialog>
      )}
    </div>
  );
}
