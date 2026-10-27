import Image from "next/image";
import { redirect } from "next/navigation";
import { LoginForm } from "@/components/login-form";
import { currentUser } from "@/lib/auth";
import { safeReturnPath } from "@/lib/safe-redirect";

const fallbackMessages: Record<string, string> = {
  invalid: "Invalid email or password",
  locked: "Too many attempts. Please wait one minute and try again.",
  unavailable: "Sign in is temporarily unavailable. Please try again.",
};

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string; error?: string }> }) {
  if (await currentUser()) redirect("/overview");
  const { next, error } = await searchParams;
  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <Image className="login-logo" src="/assets/logo_dark.png" alt="VersalMotors" width={165} height={66} priority />
        <h1 id="login-title">VersalMotors Business Intelligence</h1>
        <p className="login-subtitle">Sign in to continue</p>
        <LoginForm returnTo={safeReturnPath(next)} initialMessage={error ? fallbackMessages[error] ?? fallbackMessages.unavailable : ""} />
      </section>
    </main>
  );
}
