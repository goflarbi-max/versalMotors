export default function Loading() {
  return <div className="overview-page" aria-label="Loading business overview"><header className="page-header overview-header"><div className="skeleton-title"/><div className="skeleton-line"/></header><div className="kpi-grid">{[0,1,2,3].map((item) => <div className="skeleton-block" key={item}/>)}</div></div>;
}
