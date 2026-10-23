import Image from "next/image";
import { AnalyticsIcons } from "@/components/icons";
import { currentUser } from "@/lib/auth";

const cards = [
  {
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.25"/><path d="m15.2 15.2 4.4 4.4M8 10.5l1.7 1.7 3.5-3.8"/></svg>,
    title: "Evidence you can trace",
    description: "Every finding shows the data and the query behind it.",
  },
  {
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3.8"/><path d="m19 13.5 1.6 1.2-2 3.4-1.9-.8a8 8 0 0 1-2.2 1.3l-.3 2H10l-.3-2a8 8 0 0 1-2.2-1.3l-1.9.8-2-3.4 1.6-1.2a7 7 0 0 1 0-2.6L3.6 9.7l2-3.4 1.9.8a8 8 0 0 1 2.2-1.3l.3-2h4.1l.3 2a8 8 0 0 1 2.2 1.3l1.9-.8 2 3.4-1.6 1.2a7 7 0 0 1 .1 2.6Z"/></svg>,
    title: "Advanced Analytics",
    description: "Spot unusual patterns across sales, inventory, warranty and complaints.",
  },
  {
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5.2h14a2 2 0 0 1 2 2v8.1a2 2 0 0 1-2 2h-8l-5.2 3v-3H5a2 2 0 0 1-2-2V7.2a2 2 0 0 1 2-2Z"/><path d="M7.5 9.2h9M7.5 13h6.2"/></svg>,
    title: "Ask in plain language",
    description: "Get answers grounded in your own business data, with the facts kept separate from opinion.",
  },
];

export default async function LandingPage() {
  const user = await currentUser();
  return (
    <main className="public-landing">
      <section className="landing-hero">
        <div className="dot-wave" aria-hidden="true" />
        <header className="landing-topbar">
          <Image src="/assets/logo_light.png" alt="VersalMotors" width={218} height={87} priority />
          <a href={user ? "/overview" : "/login"} className="landing-sign-in">Sign in</a>
        </header>
        <div className="landing-copy">
          <h1>Analyze Your Data with Precision</h1>
          <p>
            VersalMotors Business Intelligence brings sales, inventory, servicing,
            warranty claims, complaints and customer satisfaction into one clear view.
            Spot what is changing, investigate the cause, and make decisions backed by
            evidence from your own data.
          </p>
          <AnalyticsIcons />
        </div>
      </section>
      <section className="landing-band" aria-label="System capabilities">
        <div className="landing-cards">
          {cards.map((card) => (
            <article className="landing-card" key={card.title}>
              <span className="landing-card-icon" aria-hidden="true">{card.icon}</span>
              <div><h2>{card.title}</h2><p>{card.description}</p></div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
