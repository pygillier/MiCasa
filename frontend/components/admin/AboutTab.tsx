"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";

const GITHUB_URL = "https://github.com/pygillier/micasa";
const WEBSITE_URL = "https://pygillier.me";

export default function AboutTab() {
  const { t } = useI18n();
  const [backend, setBackend] = useState("…");

  useEffect(() => {
    api<{ version: string }>("/admin/about").then((a) => setBackend(a.version)).catch(() => setBackend("?"));
  }, []);

  return (
    <div className="about">
      <Image src="/logo.svg" alt="MiCasa" width={147} height={44} unoptimized className="admin-logo about-logo logo-light" />
      <Image src="/logo-dark.svg" alt="MiCasa" width={147} height={44} unoptimized className="admin-logo about-logo logo-dark" />
      <dl className="about-versions">
        <dt>{t("about.backend")}</dt><dd>{backend}</dd>
        <dt>{t("about.frontend")}</dt><dd>{process.env.NEXT_PUBLIC_APP_VERSION}</dd>
      </dl>
      <div className="about-links">
        <a className="btn btn-secondary" href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
          <i className="ph-bold ph-github-logo" /> {t("about.github")}
        </a>
        <a className="btn btn-secondary" href={WEBSITE_URL} target="_blank" rel="noopener noreferrer">
          <i className="ph-bold ph-globe" /> {t("about.website")}
        </a>
      </div>
    </div>
  );
}
