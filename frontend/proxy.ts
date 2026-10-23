import { NextRequest, NextResponse } from "next/server";

const protectedRoutes = [
  "/overview",
  "/investigate",
  "/ask-the-business",
  "/management-brief",
  "/data-quality",
];

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const hasSession = Boolean(request.cookies.get("versal_session")?.value);
  const isProtected = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (isProtected && !hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/overview/:path*",
    "/investigate/:path*",
    "/ask-the-business/:path*",
    "/management-brief/:path*",
    "/data-quality/:path*",
  ],
};
