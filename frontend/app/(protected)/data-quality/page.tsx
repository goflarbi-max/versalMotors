import { DataQualityDashboard } from "@/components/data-quality-dashboard";

export default function Page() {
  return <div className="quality-page"><header className="page-header quality-header"><h1>Data Quality Report</h1><p>Built from the cleaning log and live validation checks for missing values, duplicates, unknown models, invalid dates, and orphan records.</p></header><DataQualityDashboard/></div>;
}
