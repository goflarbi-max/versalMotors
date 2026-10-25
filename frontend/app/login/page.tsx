import Image from "next/image";
import { redirect } from "next/navigation";
import { LoginForm } from "@/components/login-form";
import { currentUser } from "@/lib/auth";
import { safeReturnPath } from "@/lib/safe-redirect";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  if (await currentUser()) redirect("/overview");
  const { next } = await searchParams;
  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <Image className="login-logo" src="/assets/logo_dark.png" alt="VersalMotors" width={165} height={66} priority />
        <h1 id="login-title">VersalMotors Business Intelligence</h1>
        <p className="login-subtitle">Sign in to continue</p>
        <LoginForm returnTo={safeReturnPath(next)} />
      </section>
    </main>
  );
}
