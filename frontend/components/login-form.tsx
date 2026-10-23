"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { EyeIcon, EyeOffIcon, LockIcon, MailIcon } from "@/components/icons";

type Problem = { message?: string };

export function LoginForm() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [info, setInfo] = useState(false);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setMessage("");
    setInfo(false);
    const form = new FormData(event.currentTarget);
    try {
      const csrfResponse = await fetch("/api/v1/auth/csrf", { credentials: "include" });
      if (!csrfResponse.ok) throw new Error("Sign in is temporarily unavailable");
      const csrf = await csrfResponse.json() as { csrf_token: string };
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf.csrf_token },
        body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
      });
      if (!response.ok) {
        const problem = await response.json() as Problem;
        throw new Error(problem.message ?? "Invalid email or password");
      }
      router.replace("/overview");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Sign in is temporarily unavailable");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={submit} noValidate>
      <label className="login-field">Email Address
        <span className="input-shell"><MailIcon /><input name="email" type="email" placeholder="Enter your email" autoComplete="email" required /></span>
      </label>
      <label className="login-field">Password
        <span className="input-shell"><LockIcon /><input name="password" type={showPassword ? "text" : "password"} placeholder="Enter your password" autoComplete="current-password" required />
          <button className="password-toggle" type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOffIcon /> : <EyeIcon />}</button>
        </span>
      </label>
      <button className="forgot-button" type="button" onClick={() => { setInfo(true); setMessage("Please contact the system administrator to reset your password."); }}>Forgot Password?</button>
      <button className="sign-in-button" type="submit" disabled={pending}>{pending ? "Signing in…" : "Sign In"}</button>
      {message ? <p className={`login-message${info ? " info" : ""}`} role="status">{message}</p> : null}
    </form>
  );
}
