import Image from "next/image";
import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <Image className="login-logo" src="/assets/logo_dark.png" alt="VersalMotors" width={165} height={66} priority />
        <h1 id="login-title">VersalMotors Business Intelligence</h1>
        <p className="login-subtitle">Sign in to continue</p>
        <LoginForm />
      </section>
    </main>
  );
}
