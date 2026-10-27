import { NextRequest, NextResponse } from "next/server";
import { safeReturnPath } from "@/lib/safe-redirect";

const apiOrigin = (process.env.API_ORIGIN ?? process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

function trustedRequestOrigins(request: NextRequest) {
  const protocol = (request.headers.get("x-forwarded-proto") ?? request.nextUrl.protocol.replace(":", "")).split(",", 1)[0].trim();
  const hosts = [request.headers.get("x-forwarded-host"), request.headers.get("host")]
    .map((value) => value?.split(",", 1)[0].trim())
    .filter((value): value is string => Boolean(value));
  return [...new Set([...hosts.map((host) => `${protocol}://${host}`), request.nextUrl.origin])];
}

function isTrustedOrigin(origin: string, trustedOrigins: string[]) {
  if (trustedOrigins.includes(origin)) return true;
  try {
    const candidate = new URL(origin);
    const loopbackHosts = new Set(["localhost", "127.0.0.1", "[::1]"]);
    return loopbackHosts.has(candidate.hostname) && trustedOrigins.some((trusted) => {
      const expected = new URL(trusted);
      return loopbackHosts.has(expected.hostname) && candidate.port === expected.port;
    });
  } catch {
    return false;
  }
}

function publicOrigin(request: NextRequest) {
  const trustedOrigins = trustedRequestOrigins(request);
  const origin = request.headers.get("origin");
  return origin && isTrustedOrigin(origin, trustedOrigins) ? origin : trustedOrigins[0] ?? request.nextUrl.origin;
}

function loginRedirect(request: NextRequest, error: string, returnTo: string) {
  const url = new URL("/login", publicOrigin(request));
  url.searchParams.set("error", error);
  if (returnTo !== "/overview") url.searchParams.set("next", returnTo);
  return NextResponse.redirect(url, 303);
}

export async function POST(request: NextRequest) {
  const returnToFallback = "/overview";
  try {
    const origin = request.headers.get("origin");
    const appOrigin = publicOrigin(request);
    if (!origin || !isTrustedOrigin(origin, trustedRequestOrigins(request))) {
      return loginRedirect(request, "unavailable", returnToFallback);
    }

    const form = await request.formData();
    const email = String(form.get("email") ?? "").trim().toLowerCase();
    const password = String(form.get("password") ?? "");
    const rememberMe = form.get("remember_me") === "on";
    const returnTo = safeReturnPath(String(form.get("next") ?? returnToFallback));

    const csrfResponse = await fetch(`${apiOrigin}/api/v1/auth/csrf`, { cache: "no-store" });
    if (!csrfResponse.ok) return loginRedirect(request, "unavailable", returnTo);
    const csrf = await csrfResponse.json() as { csrf_token: string };

    const loginResponse = await fetch(`${apiOrigin}/api/v1/auth/login`, {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        "Cookie": `versal_csrf=${csrf.csrf_token}`,
        "Origin": origin,
        "X-CSRF-Token": csrf.csrf_token,
      },
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    });

    if (!loginResponse.ok) {
      return loginRedirect(request, loginResponse.status === 429 ? "locked" : loginResponse.status < 500 ? "invalid" : "unavailable", returnTo);
    }

    const response = NextResponse.redirect(new URL(returnTo, appOrigin), 303);
    for (const cookie of loginResponse.headers.getSetCookie()) {
      response.headers.append("Set-Cookie", cookie);
    }
    return response;
  } catch {
    return loginRedirect(request, "unavailable", returnToFallback);
  }
}
