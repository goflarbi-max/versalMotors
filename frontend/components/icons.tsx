import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

function IconBase({ children, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>
      {children}
    </svg>
  );
}

export const HomeIcon = (props: IconProps) => <IconBase {...props}><path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10M9 20v-6h6v6"/></IconBase>;
export const OverviewIcon = (props: IconProps) => <IconBase {...props}><rect x="3" y="3" width="7" height="8" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="3" y="15" width="7" height="6" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/></IconBase>;
export const SearchIcon = (props: IconProps) => <IconBase {...props}><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5M7.5 13v-3m3 3V7m3 6v-2"/></IconBase>;
export const ChatIcon = (props: IconProps) => <IconBase {...props}><path d="M4 5h16v12H8l-4 3V5Z"/><path d="M8 9h8M8 13h5"/></IconBase>;
export const BriefIcon = (props: IconProps) => <IconBase {...props}><path d="M6 3h8l4 4v14H6V3Z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></IconBase>;
export const QualityIcon = (props: IconProps) => <IconBase {...props}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 11 2 2 4-5M15 10h3M15 14h3"/></IconBase>;
export const SunIcon = (props: IconProps) => <IconBase {...props}><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></IconBase>;
export const MoonIcon = (props: IconProps) => <IconBase {...props}><path d="M20.5 15.5A9 9 0 0 1 8.5 3.5a9 9 0 1 0 12 12Z"/></IconBase>;
export const LogoutIcon = (props: IconProps) => <IconBase {...props}><path d="M10 5H5v14h5M14 8l4 4-4 4M18 12H9"/></IconBase>;
export const CloseIcon = (props: IconProps) => <IconBase {...props}><path d="m6 6 12 12M18 6 6 18"/></IconBase>;
export const EyeIcon = (props: IconProps) => <IconBase {...props}><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></IconBase>;
export const EyeOffIcon = (props: IconProps) => <IconBase {...props}><path d="m3 3 18 18M10.6 6.2A10.6 10.6 0 0 1 12 6c6.5 0 10 6 10 6a17 17 0 0 1-2.1 2.8M6.2 6.2A15.6 15.6 0 0 0 2 12s3.5 6 10 6c1 0 2-.2 2.8-.5M9.9 9.9a3 3 0 0 0 4.2 4.2"/></IconBase>;
export const MailIcon = (props: IconProps) => <IconBase {...props}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></IconBase>;
export const LockIcon = (props: IconProps) => <IconBase {...props}><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></IconBase>;

export function AnalyticsIcons() {
  return (
    <div className="analytics-icons" aria-hidden="true">
      <span><IconBase><path d="M4 20h16M6 17v-6h3v6m3 0V6h3v11m3 0V9h3v8"/></IconBase></span>
      <span><IconBase><path d="M4 20h16M5 16l4-4 3 2.5 6-7M15 7.5h3v3"/></IconBase></span>
      <span><IconBase><path d="M11 4a8 8 0 1 0 8 8h-8V4Z"/><path d="M14 4v5h5a8 8 0 0 0-5-5Z"/></IconBase></span>
      <span><IconBase><path d="M4.5 18a8 8 0 0 1 15 0M7 15l-1.5-1.2M17 15l1.5-1.2M12 12V8m0 9 3.5-4.5"/></IconBase></span>
      <span><IconBase><path d="M4 18V6h12v7M7 15l2.5-3 2 2 3-4"/><circle cx="16.5" cy="16.5" r="3.5"/><path d="m19 19 2 2"/></IconBase></span>
    </div>
  );
}
