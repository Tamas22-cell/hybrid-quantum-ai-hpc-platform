export async function backendFetch(path, request, init = {}) {
  const base = process.env.HPC_API_URL?.replace(/\/$/, "");
  if (!base) return Response.json({ error: "Backend not configured" }, { status: 503 });

  const headers = new Headers(init.headers || {});
  const cookie = request?.headers.get("cookie");
  const forwardedFor = request?.headers.get("x-forwarded-for");
  if (cookie) headers.set("cookie", cookie);
  if (forwardedFor) headers.set("x-forwarded-for", forwardedFor);
  if (request?.headers.get("x-real-ip")) headers.set("x-real-ip", request.headers.get("x-real-ip"));

  try {
    return await fetch(`${base}${path}`, {
      ...init,
      headers,
      cache: "no-store",
      signal: init.signal || AbortSignal.timeout(15000),
    });
  } catch {
    return Response.json({ error: "Backend unavailable" }, { status: 502 });
  }
}

export async function forwardJson(path, request, init = {}) {
  const response = await backendFetch(path, request, init);
  const body = await response.text();
  return new Response(body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") || "application/json",
      "Cache-Control": "no-store",
    },
  });
}

export function sessionCookie(token, request, clear = false) {
  const secure = new URL(request.url).protocol === "https:";
  const maxAge = clear ? 0 : 60 * 60 * 24 * 7;
  const value = clear ? "" : token;
  return `hpc_session=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${secure ? "; Secure" : ""}`;
}

export async function establishSession(path, request) {
  let input;
  try {
    input = await request.json();
  } catch {
    return Response.json({ error: "Invalid request" }, { status: 400 });
  }

  const response = await backendFetch(path, request, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.HPC_API_KEY || "",
      "X-Client-IP": request.headers.get("x-real-ip") || request.headers.get("x-forwarded-for") || "",
    },
    body: JSON.stringify(input),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    return Response.json({ error: data.detail || data.error || "Authentication failed" }, { status: response.status });
  }
  if (!data.session_token || !data.user) {
    return Response.json({ error: "Invalid authentication response" }, { status: 502 });
  }

  return Response.json({ user: data.user }, {
    headers: { "Set-Cookie": sessionCookie(data.session_token, request) },
  });
}
