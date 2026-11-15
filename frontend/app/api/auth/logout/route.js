import { backendFetch, sessionCookie } from "../../../../hpc-backend.js";

export async function POST(request) {
  const response = await backendFetch("/auth/logout", request, { method: "POST" });
  return Response.json({ ok: true }, {
    status: response.ok ? 200 : response.status,
    headers: { "Set-Cookie": sessionCookie("", request, true), "Cache-Control": "no-store" },
  });
}
