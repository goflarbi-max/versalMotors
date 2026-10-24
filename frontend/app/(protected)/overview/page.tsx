import { OverviewDashboard } from "@/components/overview-dashboard";

export default function Page() {
  return <div className="overview-page">
    <header className="page-header overview-header"><h1>Business overview</h1><p>A management view of sales scale, profitability, discounting, and where performance comes from.</p></header>
    <OverviewDashboard />
  </div>;
}
