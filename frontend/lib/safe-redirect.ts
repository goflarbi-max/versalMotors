export function safeReturnPath(value: string | null | undefined, fallback = "/overview"): string {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return fallback;
  try {
    const parsed = new URL(value, "https://versalmotors.local");
    if (parsed.origin !== "https://versalmotors.local") return fallback;
    return `${parsed.pathname}${parsed.search}${parsed.hash}`;
  } catch {
    return fallback;
  }
}
