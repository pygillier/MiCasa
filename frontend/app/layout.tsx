import type { Metadata } from "next";
import { headers } from "next/headers";
import { I18nProvider } from "@/components/I18nProvider";
import { negotiateLocale } from "@/lib/i18n/messages";
import { getTheme } from "@/lib/server";
import "@phosphor-icons/web/regular";
import "@phosphor-icons/web/light";
import "./nocturne.css";
import "./themes.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "MiCasa",
  description: "Personal startpage",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const locale = negotiateLocale((await headers()).get("accept-language"));
  const theme = await getTheme();
  return (
    <html lang={locale} data-theme={theme}>
      <body>
        <I18nProvider locale={locale}>{children}</I18nProvider>
      </body>
    </html>
  );
}
