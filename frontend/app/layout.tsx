import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
  fallback: ["system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
});

export const metadata: Metadata = {
  title: "VersalMotors Business Intelligence",
  description: "Automotive business intelligence and decision support.",
  icons: { icon: "/assets/logo_dark.png" },
};

const themeBootstrap = `
(() => {
  try {
    const stored = localStorage.getItem('versal_theme');
    const cookie = document.cookie.match(/(?:^|; )versal_theme=(light|dark)/)?.[1];
    const theme = stored === 'dark' || cookie === 'dark' ? 'dark' : 'light';
    document.documentElement.dataset.theme = theme;
  } catch (_) {
    document.documentElement.dataset.theme = 'light';
  }
})();`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-theme="light" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeBootstrap }} />
      </head>
      <body className={inter.variable}>{children}</body>
    </html>
  );
}
