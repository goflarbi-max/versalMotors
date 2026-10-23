import "server-only";

import { cookies } from "next/headers";

export type CurrentUser = { authenticated: true; email: string };

const backendUrl = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export async function currentUser(): Promise<CurrentUser | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  if (!cookieHeader.includes("versal_session=")) return null;
  try {
    const response = await fetch(`${backendUrl}/api/v1/auth/me`, {
      headers: { Cookie: cookieHeader },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return await response.json() as CurrentUser;
  } catch {
    return null;
  }
}
