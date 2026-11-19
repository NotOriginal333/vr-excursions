import Link from "next/link";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata = { title: "VR-екскурсії для уроків" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="uk">
      <body>
        <header>
          <Link href="/">VR-екскурсії для уроків</Link>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
