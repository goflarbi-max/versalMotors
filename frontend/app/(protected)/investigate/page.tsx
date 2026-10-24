import { InvestigateDashboard } from "@/components/investigate-dashboard";

export default function Page() {
  return <div className="investigate-page">
    <header className="page-header investigate-header"><h1>Investigate warranty costs</h1><p>Move from the overall signal to the models, branches, and individual claims underneath it.</p></header>
    <InvestigateDashboard />
  </div>;
}
