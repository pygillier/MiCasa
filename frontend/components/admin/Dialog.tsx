"use client";

import { useEffect, type FormEvent, type ReactNode } from "react";
import { useI18n } from "@/components/I18nProvider";

/** Modal form with the standard cancel / save actions. */
export default function Dialog({
  title, onClose, onSubmit, children,
}: { title: string; onClose: () => void; onSubmit: (e: FormEvent) => void; children: ReactNode }) {
  const { t } = useI18n();
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div className="dialog-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="dialog" role="dialog" aria-modal="true" aria-label={title}>
        <div className="dialog-title">{title}</div>
        <form className="form-grid" onSubmit={onSubmit}>
          {children}
          <div className="dialog-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>{t("common.cancel")}</button>
            <button type="submit" className="btn btn-primary">{t("common.save")}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
