import "server-only";

import { cookies } from "next/headers";

export type CurrentUser = { authenticated: true; email: string; role: "viewer" | "admin" };

const apiOrigin = (process.env.API_ORIGIN ?? process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export async function currentUser(): Promise<CurrentUser | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  if (!cookieHeader.includes("versal_session=")) return null;
  try {
    const response = await fetch(`${apiOrigin}/api/auth/me`, {
      headers: { Cookie: cookieHeader },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return await response.json() as CurrentUser;
  } catch {
    return null;
  }
}
