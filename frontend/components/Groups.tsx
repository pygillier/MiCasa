"use client";

import { useI18n } from "@/components/I18nProvider";
import type { Group, StartLink } from "@/lib/types";

function StatusDot({ link }: { link: StartLink }) {
  const { t } = useI18n();
  if (!link.status) return null;
  const status = ["up", "down", "pending", "maintenance"].includes(link.status)
    ? t(`status.${link.status}` as "status.up")
    : link.status;
  const cls =
    link.status === "up" ? "dot-up" : link.status === "down" ? "dot-down" : "dot-idle";
  const label = t("status.label", { status });
  const dot = <span className={`dot ${cls}`} title={label} aria-label={t("status.aria", { status })} />;
  return link.status_url ? (
    <a href={link.status_url} target="_blank" rel="noreferrer" title={label}
       aria-label={t("status.ariaOpen", { status })} className={`dot ${cls}`} />
  ) : (
    dot
  );
}

export default function Groups({ groups }: { groups: Group[] }) {
  const { t } = useI18n();
  if (groups.length === 0) return <p className="empty">{t("groups.empty")}</p>;
  return (
    <>
      {groups.map((g) => (
        <section key={g.id}>
          <span className="group-mark" />
          <div className="group-head">
            <div className="group-name">{g.name}</div>
            <div className="group-note">{g.note}</div>
          </div>
          <div className="links">
            {g.items.map((it) => (
              <div className="link" key={it.id}>
                <a className="link-a" href={it.url}>
                  <span className="link-icon">
                    <i className={`ph ${it.icon}`} />
                  </span>
                  <span className="link-label">{it.label}</span>
                </a>
                <StatusDot link={it} />
                <span className="link-host">{it.host}</span>
              </div>
            ))}
          </div>
        </section>
      ))}
    </>
  );
}
