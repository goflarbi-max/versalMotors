import { ApiEnvelope } from "@/lib/overview";

type Problem = { message?: string };

export async function protectedPost<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const csrfResponse = await fetch("/api/v1/auth/csrf", { credentials: "include", signal });
  if (!csrfResponse.ok) throw new Error("The request service is temporarily unavailable.");
  const { csrf_token } = await csrfResponse.json() as { csrf_token: string };
  const response = await fetch(path, {
    method: "POST",
    credentials: "include",
    signal,
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf_token },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const problem = await response.json().catch(() => ({})) as Problem;
    throw new Error(problem.message ?? "The request could not be completed.");
  }
  return (await response.json() as ApiEnvelope<T>).data;
}
