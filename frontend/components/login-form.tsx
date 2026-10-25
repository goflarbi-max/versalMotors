"use client";

import { FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { EyeIcon, EyeOffIcon, LockIcon, MailIcon } from "@/components/icons";
import { safeReturnPath } from "@/lib/safe-redirect";

export function LoginForm({ returnTo = "/overview" }: { returnTo?: string }) {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [info, setInfo] = useState(false);
  const [pending, setPending] = useState(false);
  const messageRef = useRef<HTMLParagraphElement>(null);

  function showMessage(text: string, isInfo = false) {
    setInfo(isInfo);
    setMessage(text);
    window.requestAnimationFrame(() => messageRef.current?.focus());
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    setPending(true);
    setMessage("");
    setInfo(false);
    const form = new FormData(event.currentTarget);
    try {
      const csrfResponse = await fetch("/api/v1/auth/csrf", { credentials: "include" });
      if (!csrfResponse.ok) throw new Error("Sign in is temporarily unavailable. Please try again.");
      const csrf = await csrfResponse.json() as { csrf_token: string };
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf.csrf_token },
        body: JSON.stringify({
          email: String(form.get("email") ?? "").trim().toLowerCase(),
          password: String(form.get("password") ?? ""),
        }),
      });
      if (!response.ok) {
        if (response.status === 429) {
          const seconds = Number(response.headers.get("Retry-After") ?? "900");
          const minutes = Math.max(1, Math.ceil(seconds / 60));
          throw new Error(`Too many attempts. Try again in ${minutes} minute${minutes === 1 ? "" : "s"}.`);
        }
        if (response.status === 400 || response.status === 401 || response.status === 422) {
          throw new Error("Invalid email or password");
        }
        throw new Error("Sign in is temporarily unavailable. Please try again.");
      }
      router.replace(safeReturnPath(returnTo));
      router.refresh();
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Sign in is temporarily unavailable. Please try again.");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={submit} noValidate>
      <label className="login-field" htmlFor="login-email">Email Address</label>
      <span className="input-shell"><MailIcon /><input id="login-email" name="email" type="email" maxLength={254} placeholder="Enter your email" autoComplete="username" required /></span>
      <label className="login-field" htmlFor="login-password">Password</label>
      <span className="input-shell"><LockIcon /><input id="login-password" name="password" maxLength={128} type={showPassword ? "text" : "password"} placeholder="Enter your password" autoComplete="current-password" required />
        <button className="password-toggle" type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOffIcon /> : <EyeIcon />}</button>
      </span>
      <button className="forgot-button" type="button" onClick={() => showMessage("Please contact the system administrator to reset your password.", true)}>Forgot Password?</button>
      <button className="sign-in-button" type="submit" disabled={pending} aria-disabled={pending}>{pending ? "Signing in..." : "Sign In"}</button>
      {message ? <p ref={messageRef} className={`login-message${info ? " info" : ""}`} role="alert" aria-live="assertive" tabIndex={-1}>{message}</p> : null}
      <p className="demo-access"><strong>Demo access</strong><br />Email: demo@versalmotors.com<br />Password: VersalDemo2026!</p>
    </form>
  );
}
