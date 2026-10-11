"use client";

import { useEffect, useState } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import type { JobRun } from "@/lib/types";
import type { MessageKey } from "@/lib/i18n/messages";

const JOB_IDS = ["refresh_weather", "refresh_kuma"];
const PAGE_SIZE = 10;

export default function JobsTab() {
  const { t, locale } = useI18n();
  const [runs, setRuns] = useState<JobRun[]>([]);
  const [page, setPage] = useState(0);

  useEffect(() => {
    api<JobRun[]>("/admin/jobs").then(setRuns).catch(() => {});
  }, []);

  const pages = Math.max(1, Math.ceil(runs.length / PAGE_SIZE));
  const current = Math.min(page, pages - 1);
  const visible = runs.slice(current * PAGE_SIZE, (current + 1) * PAGE_SIZE);

  return (
    <div>
      <h3 className="section-title">{t("settings.runs")}</h3>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>{t("settings.job")}</th><th>{t("settings.when")}</th><th>{t("settings.status")}</th><th>{t("settings.message")}</th></tr></thead>
          <tbody>
            {visible.map((r) => (
              <tr key={r.id}>
                <td>{JOB_IDS.includes(r.job_id) ? t(`settings.job.${r.job_id}` as MessageKey) : r.job_id}</td>
                <td className="muted">{new Date(r.started_at).toLocaleString(locale)}</td>
                <td><span className={`tag ${r.status === "ok" ? "tag-accent" : "tag-neutral"}`}>{r.status}</span></td>
                <td className="muted">{r.message}</td>
              </tr>
            ))}
            {runs.length === 0 && <tr><td colSpan={4} className="muted">{t("settings.noRuns")}</td></tr>}
          </tbody>
        </table>
      </div>
      {runs.length > PAGE_SIZE && (
        <div className="toolbar">
          <button type="button" className="btn btn-secondary" disabled={current === 0}
                  onClick={() => setPage(current - 1)}>
            <i className="ph ph-caret-left" /> {t("settings.prev")}
          </button>
          <span className="muted">{t("settings.page", { page: current + 1, pages })}</span>
          <button type="button" className="btn btn-secondary" disabled={current >= pages - 1}
                  onClick={() => setPage(current + 1)}>
            {t("settings.next")} <i className="ph ph-caret-right" />
          </button>
        </div>
      )}
    </div>
  );
}
