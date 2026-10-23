import Image from "next/image";
import { AnalyticsIcons } from "@/components/icons";
import { currentUser } from "@/lib/auth";

const cards = [
  {
    icon: "✓",
    title: "Evidence you can trace",
    description: "Every finding shows the data and the query behind it.",
  },
  {
    icon: "⌁",
    title: "Advanced Analytics",
    description: "Spot unusual patterns across sales, inventory, warranty and complaints.",
  },
  {
    icon: "◇",
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
