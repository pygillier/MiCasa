import type { Metadata } from "next";
import { headers } from "next/headers";
import { I18nProvider } from "@/components/I18nProvider";
import { negotiateLocale } from "@/lib/i18n/messages";
import { getSiteTitle, getThemes } from "@/lib/server";
import { THEME_SCRIPT } from "@/lib/themes";
import "@fontsource/open-sans/latin-400.css";
import "@fontsource/open-sans/latin-500.css";
import "@fontsource/open-sans/latin-600.css";
import "@fontsource/open-sans/latin-700.css";
import "@phosphor-icons/web/bold";
import "./nocturne.css";
import "./themes.css";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  return { title: await getSiteTitle(), description: "Personal startpage" };
}

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const locale = negotiateLocale((await headers()).get("accept-language"));
  const { night, day } = await getThemes();
  return (
    <html lang={locale} data-theme={night} data-theme-night={night} data-theme-day={day} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body>
        <I18nProvider locale={locale}>{children}</I18nProvider>
      </body>
    </html>
  );
}
