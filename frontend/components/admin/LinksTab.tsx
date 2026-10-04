"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api } from "@/lib/api";
import type { AdminLink, Category, Monitor } from "@/lib/types";
import Dialog from "./Dialog";

type Draft = Partial<AdminLink>;

export default function LinksTab() {
  const [cats, setCats] = useState<Category[]>([]);
  const [links, setLinks] = useState<AdminLink[]>([]);
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [monitorError, setMonitorError] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(
    () =>
      Promise.all([api<Category[]>("/admin/categories"), api<AdminLink[]>("/admin/links")])
        .then(([c, l]) => {
          setCats(c);
          setLinks(l);
        })
        .catch((e) => setError(e.message)),
    [],
  );

  useEffect(() => {
    load();
    api<Monitor[]>("/admin/kuma/monitors")
      .then(setMonitors)
      .catch((e) => setMonitorError(e.message));
  }, [load]);

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!draft) return;
    const body = { ...draft, kuma_monitor_id: draft.kuma_monitor_id ?? null };
    try {
      if (draft.id) await api(`/admin/links/${draft.id}`, { method: "PUT", body });
      else await api("/admin/links", { method: "POST", body });
      setDraft(null);
      setError("");
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function remove(l: AdminLink) {
    if (!window.confirm(`Delete "${l.label}"?`)) return;
    await api(`/admin/links/${l.id}`, { method: "DELETE" }).catch((e) => setError(e.message));
    load();
  }

  async function move(catId: number, i: number, d: -1 | 1) {
    const group = links.filter((l) => l.category_id === catId);
    [group[i], group[i + d]] = [group[i + d], group[i]];
    setLinks([...links.filter((l) => l.category_id !== catId), ...group]);
    await api("/admin/links/reorder", { method: "PUT", body: { ids: group.map((l) => l.id) } });
  }

  const monitorName = (id: number | null) =>
    id === null ? "" : (monitors.find((m) => m.id === id)?.name ?? `#${id}`);

  return (
    <div className="form-grid">
      <div className="toolbar">
        <span className="spacer muted">{links.length} links</span>
        <button className="btn btn-primary" disabled={cats.length === 0}
                onClick={() => setDraft({ category_id: cats[0]?.id, icon: "ph-link", is_public: false })}>
          <i className="ph ph-plus" /> New link
        </button>
      </div>
      {cats.length === 0 && <div className="muted">Create a category first.</div>}
      {error && <div className="error">{error}</div>}

      {cats.map((c) => {
        const group = links.filter((l) => l.category_id === c.id);
        return (
          <div key={c.id}>
            <h3 className="section-title">{c.name}</h3>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr><th /><th>Label</th><th>URL</th><th>Monitor</th><th>Visibility</th><th /></tr>
                </thead>
                <tbody>
                  {group.map((l, i) => (
                    <tr key={l.id}>
                      <td><i className={`ph ${l.icon}`} /></td>
                      <td>{l.label}</td>
                      <td className="muted">{l.url}</td>
                      <td className="muted">{monitorName(l.kuma_monitor_id)}</td>
                      <td>
                        <span className={`tag ${l.is_public ? "tag-accent" : "tag-neutral"}`}>
                          {l.is_public ? "Public" : "Private"}
                        </span>
                      </td>
                      <td>
                        <div className="row-actions">
                          <button className="btn btn-icon small" disabled={i === 0} aria-label="Move up" onClick={() => move(c.id, i, -1)}><i className="ph ph-arrow-up" /></button>
                          <button className="btn btn-icon small" disabled={i === group.length - 1} aria-label="Move down" onClick={() => move(c.id, i, 1)}><i className="ph ph-arrow-down" /></button>
                          <button className="btn btn-icon small" aria-label="Edit" onClick={() => setDraft(l)}><i className="ph ph-pencil-simple" /></button>
                          <button className="btn btn-icon small" aria-label="Delete" onClick={() => remove(l)}><i className="ph ph-trash" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {group.length === 0 && (
                    <tr><td colSpan={6} className="muted">No links.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}

      {draft && (
        <Dialog title={draft.id ? "Edit link" : "New link"} onClose={() => setDraft(null)}>
          <form className="form-grid" onSubmit={save}>
            <div className="form-2">
              <div className="field">
                <label htmlFor="l-label">Label</label>
                <input id="l-label" className="input" required maxLength={100} value={draft.label ?? ""}
                       onChange={(e) => setDraft({ ...draft, label: e.target.value })} />
              </div>
              <div className="field">
                <label htmlFor="l-cat">Category</label>
                <select id="l-cat" className="input" value={draft.category_id}
                        onChange={(e) => setDraft({ ...draft, category_id: Number(e.target.value) })}>
                  {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
            </div>
            <div className="field">
              <label htmlFor="l-url">URL</label>
              <input id="l-url" className="input" type="url" required value={draft.url ?? ""}
                     placeholder="https://"
                     onChange={(e) => setDraft({ ...draft, url: e.target.value })} />
            </div>
            <div className="form-2">
              <div className="field">
                <label htmlFor="l-icon">
                  Icon (<a href="https://phosphoricons.com" target="_blank" rel="noreferrer">Phosphor</a> class)
                </label>
                <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "center" }}>
                  <i className={`ph ${draft.icon}`} style={{ fontSize: 20 }} />
                  <input id="l-icon" className="input" pattern="ph-[a-z0-9-]+" value={draft.icon ?? ""}
                         placeholder="ph-house-line"
                         onChange={(e) => setDraft({ ...draft, icon: e.target.value })} />
                </div>
              </div>
              <div className="field">
                <label htmlFor="l-host">Host label (optional)</label>
                <input id="l-host" className="input" maxLength={100} value={draft.host ?? ""}
                       onChange={(e) => setDraft({ ...draft, host: e.target.value })} />
              </div>
            </div>
            <div className="field">
              <label htmlFor="l-mon">Uptime Kuma monitor</label>
              <select id="l-mon" className="input" value={draft.kuma_monitor_id ?? ""}
                      onChange={(e) => setDraft({ ...draft, kuma_monitor_id: e.target.value === "" ? null : Number(e.target.value) })}>
                <option value="">None</option>
                {draft.kuma_monitor_id != null && !monitors.some((m) => m.id === draft.kuma_monitor_id) && (
                  <option value={draft.kuma_monitor_id}>#{draft.kuma_monitor_id}</option>
                )}
                {monitors.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
              {monitorError && <div className="error">{monitorError}</div>}
            </div>
            <label className="check">
              <input type="checkbox" checked={!!draft.is_public}
                     onChange={(e) => setDraft({ ...draft, is_public: e.target.checked })} />
              Public (also requires its category to be public)
            </label>
            <div className="dialog-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setDraft(null)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save</button>
            </div>
          </form>
        </Dialog>
      )}
    </div>
  );
}
