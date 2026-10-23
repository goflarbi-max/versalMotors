export function PagePlaceholder({ title, description }: { title: string; description: string }) {
  return (
    <>
      <header className="page-header"><h1>{title}</h1><p>{description}</p></header>
      <section className="migration-placeholder">This page shell is ready. Business content is introduced in its approved migration phase.</section>
    </>
  );
}
