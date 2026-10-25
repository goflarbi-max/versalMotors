"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useSyncExternalStore } from "react";
import {
  BriefIcon, ChatIcon, LogoutIcon, MoonIcon, OverviewIcon,
  QualityIcon, SearchIcon, SunIcon,
} from "@/components/icons";
import { BusinessFilterPanel, FilterProvider } from "@/components/filter-provider";

const navigation = [
  { href: "/overview", label: "Overview", icon: OverviewIcon },
  { href: "/investigate", label: "Investigate", icon: SearchIcon },
  { href: "/ask-the-business", label: "Ask the Business", icon: ChatIcon },
  { href: "/management-brief", label: "Management Brief", icon: BriefIcon },
  { href: "/data-quality", label: "Data Quality", icon: QualityIcon },
];

type Props = { email: string; children: React.ReactNode };

const mobileQuery = "(max-width: 640px)";
function subscribeMobile(callback: () => void) {
  const query = window.matchMedia(mobileQuery);
  query.addEventListener("change", callback);
  return () => query.removeEventListener("change", callback);
}
function mobileSnapshot() { return window.matchMedia(mobileQuery).matches; }
function subscribeTheme(callback: () => void) {
  window.addEventListener("versal-theme-change", callback);
  return () => window.removeEventListener("versal-theme-change", callback);
}
function themeSnapshot() { return document.documentElement.dataset.theme === "dark"; }

export function AppShell(props: Props) {
  const pathname = usePathname();
  const usesBusinessFilters = pathname === "/overview" || pathname === "/investigate";
  return usesBusinessFilters
    ? <FilterProvider><AppShellContent {...props} showBusinessFilters/></FilterProvider>
    : <AppShellContent {...props} showBusinessFilters={false}/>;
}

function AppShellContent({ email, children, showBusinessFilters }: Props & { showBusinessFilters: boolean }) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const mobile = useSyncExternalStore(subscribeMobile, mobileSnapshot, () => false);
  const dark = useSyncExternalStore(subscribeTheme, themeSnapshot, () => false);
  const [manualOpen, setManualOpen] = useState<boolean | null>(null);
  const open = manualOpen ?? !mobile;

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") setManualOpen(false); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = open && mobile ? "hidden" : "";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = ""; };
  }, [open, mobile]);

  function toggleTheme() {
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("versal_theme", next);
    document.cookie = `versal_theme=${next}; Max-Age=31536000; Path=/; SameSite=Lax`;
    window.dispatchEvent(new Event("versal-theme-change"));
  }

  async function signOut() {
    try {
      const csrfResponse = await fetch("/api/v1/auth/csrf", { credentials: "include" });
      const { csrf_token } = await csrfResponse.json() as { csrf_token: string };
      await fetch("/api/v1/auth/logout", {
        method: "POST", credentials: "include", headers: { "X-CSRF-Token": csrf_token },
      });
    } finally {
      document.documentElement.dataset.theme = "light";
      localStorage.setItem("versal_theme", "light");
      document.cookie = "versal_theme=light; Max-Age=31536000; Path=/; SameSite=Lax";
      router.replace("/login");
      router.refresh();
    }
  }

  return (
    <div className={`app-shell${open ? " sidebar-open" : ""}`}>
      <button className="hamburger" type="button" onClick={() => setManualOpen(!open)}
        aria-label={open ? "Close navigation menu" : "Open navigation menu"} aria-expanded={open} aria-controls="app-navigation">
        <span className="hamburger-lines" aria-hidden="true"><i/><i/><i/></span>
      </button>
      {open ? <button className="sidebar-backdrop" aria-label="Dismiss navigation menu" onClick={() => setManualOpen(false)} /> : null}
      <aside className="app-sidebar" id="app-navigation" aria-label="Primary navigation">
        <div className="sidebar-content">
          <Image className="sidebar-logo sidebar-logo-dark" src="/assets/logo_dark.png" alt="VersalMotors" width={150} height={60} />
          <Image className="sidebar-logo sidebar-logo-light" src="/assets/logo_light.png" alt="VersalMotors" width={150} height={60} />
          <nav className="sidebar-nav">
            {navigation.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;
              const query = searchParams.toString();
              const destination = `${item.href}${query ? `?${query}` : ""}`;
              return <Link key={item.href} href={destination} onClick={(event) => { if (mobile) { event.preventDefault(); router.push(destination); setManualOpen(false); } }} className={`sidebar-link${active ? " active" : ""}`} aria-current={active ? "page" : undefined}><Icon />{item.label}</Link>;
            })}
          </nav>
          <div className="sidebar-footer">
            <p className="sidebar-email"><strong>Signed in</strong><br />{email}</p>
            <button className="theme-button" type="button" onClick={toggleTheme}>{dark ? <SunIcon /> : <MoonIcon />}{dark ? "Light mode" : "Dark mode"}</button>
            <button className="logout-button" type="button" onClick={signOut}><LogoutIcon />Sign out</button>
          </div>
          {showBusinessFilters ? <BusinessFilterPanel /> : null}
        </div>
      </aside>
      <main className="app-main">{children}</main>
    </div>
  );
}
