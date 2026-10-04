import type { Metadata } from "next";
import "@phosphor-icons/web/regular";
import "@phosphor-icons/web/light";
import "./nocturne.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "MiCasa",
  description: "Personal startpage",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
