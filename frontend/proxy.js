import { NextResponse } from "next/server";

const publicPages = new Set(["/login", "/register"]);

export function proxy(request) {
  const { pathname } = request.nextUrl;
  if (pathname.startsWith("/api/") || publicPages.has(pathname)) return NextResponse.next();
  if (request.cookies.has("hpc_session")) return NextResponse.next();

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)"],
};
