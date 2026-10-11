"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";

/**
 * Shared editing state for an admin resource living at `/admin/<base>`:
 * draft dialog, save (POST/PUT), delete with confirmation and reorder.
 * `load` must be stable (wrap it in useCallback).
 */
export function useAdminCrud<D extends { id?: number }>(base: string, load: () => Promise<void>) {
  const { t } = useI18n();
  const [draft, setDraft] = useState<D | null>(null);
  const [error, setError] = useState("");

  const fail = useCallback((e: Error) => setError(e.message), []);
  const reload = useCallback(() => load().catch(fail), [load, fail]);

  useEffect(() => {
    reload();
  }, [reload]);

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!draft) return;
    try {
      if (draft.id) await api(`/admin/${base}/${draft.id}`, { method: "PUT", body: draft });
      else await api(`/admin/${base}`, { method: "POST", body: draft });
      setDraft(null);
      setError("");
      reload();
    } catch (err) {
      fail(err as Error);
    }
  }

  async function remove(id: number, confirmKey: Parameters<typeof t>[0], vars: Parameters<typeof t>[1]) {
    if (!window.confirm(t(confirmKey, vars))) return;
    await api(`/admin/${base}/${id}`, { method: "DELETE" }).catch(fail);
    reload();
  }

  function reorder(ids: number[]) {
    api(`/admin/${base}/reorder`, { method: "PUT", body: { ids } }).catch((e) => {
      fail(e);
      reload();
    });
  }

  return { draft, setDraft, error, save, remove, reorder };
}
