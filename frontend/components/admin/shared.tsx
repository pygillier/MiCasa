"use client";

import type { InputHTMLAttributes, ReactNode } from "react";
import { useI18n } from "@/components/I18nProvider";

export type Msg = { ok: boolean; text: string };

export function Notice({ msg }: { msg: Msg | null }) {
  return msg && <span className={msg.ok ? "ok" : "error"}>{msg.text}</span>;
}

export function Field({ id, label, children }: { id: string; label: ReactNode; children: ReactNode }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children}
    </div>
  );
}

type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id" | "value" | "onChange">;

export function TextField({
  id, label, value, onChange, ...input
}: { id: string; label: ReactNode; value: string; onChange: (v: string) => void } & InputProps) {
  return (
    <Field id={id} label={label}>
      <input id={id} className="input" value={value} onChange={(e) => onChange(e.target.value)} {...input} />
    </Field>
  );
}

export function VisibilityTag({ isPublic }: { isPublic: boolean }) {
  const { t } = useI18n();
  return (
    <span className={`tag ${isPublic ? "tag-accent" : "tag-neutral"}`}>
      {isPublic ? t("common.public") : t("common.private")}
    </span>
  );
}

export function RowActions({
  index, count, onMove, onEdit, onDelete,
}: {
  index: number;
  count: number;
  onMove: (delta: -1 | 1) => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const { t } = useI18n();
  const btn = (icon: string, label: string, onClick: () => void, disabled = false) => (
    <button className="btn btn-icon small" disabled={disabled} aria-label={label} onClick={onClick}>
      <i className={`ph-bold ${icon}`} />
    </button>
  );
  return (
    <div className="row-actions">
      {btn("ph-arrow-up", t("common.moveUp"), () => onMove(-1), index === 0)}
      {btn("ph-arrow-down", t("common.moveDown"), () => onMove(1), index === count - 1)}
      {btn("ph-pencil-simple", t("common.edit"), onEdit)}
      {btn("ph-trash", t("common.delete"), onDelete)}
    </div>
  );
}

/** Swap `list[i]` with `list[i + delta]` in a copy. */
export function swap<T>(list: T[], i: number, delta: -1 | 1): T[] {
  const next = [...list];
  [next[i], next[i + delta]] = [next[i + delta], next[i]];
  return next;
}
