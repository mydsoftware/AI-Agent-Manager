interface Env {
  GATEWAY_TOKEN: string;
  MANAGER_API_URL: string;
  MANAGER_API_KEY: string;
}

const jsonHeaders = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
};

function response(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: jsonHeaders });
}

function bearer(request: Request): string | null {
  const value = request.headers.get("authorization");
  if (!value?.startsWith("Bearer ")) return null;
  return value.slice(7).trim() || null;
}

async function constantTimeEqual(a: string, b: string): Promise<boolean> {
  const encoder = new TextEncoder();
  const left = await crypto.subtle.digest("SHA-256", encoder.encode(a));
  const right = await crypto.subtle.digest("SHA-256", encoder.encode(b));
  const x = new Uint8Array(left);
  const y = new Uint8Array(right);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

function validUrl(value: unknown): value is string {
  if (typeof value !== "string" || value.length > 2048) return false;
  try {
    const url = new URL(value);
    return url.protocol === "https:";
  } catch {
    return false;
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "POST, GET, OPTIONS",
          "access-control-allow-headers": "authorization, content-type",
        },
      });
    }

    const url = new URL(request.url);

    if (url.pathname === "/health" && request.method === "GET") {
      return response({ status: "فعال" });
    }

    if (url.pathname !== "/execute/website-audit" || request.method !== "POST") {
      return response({ error: "مسیر درخواست پیدا نشد." }, 404);
    }

    const supplied = bearer(request);
    if (!supplied || !(await constantTimeEqual(supplied, env.GATEWAY_TOKEN))) {
      return response({ error: "دسترسی غیرمجاز است." }, 401);
    }

    let body: Record<string, unknown>;
    try {
      body = await request.json();
    } catch {
      return response({ error: "JSON نامعتبر است." }, 400);
    }

    const requestId = typeof body.request_id === "string" ? body.request_id.trim() : "";
    const target = body.url;
    const mode = typeof body.mode === "string" ? body.mode.trim() : "pre_contract";
    const access = body.access === true;
    const language = typeof body.language === "string" ? body.language : "fa";
    const description = typeof body.description === "string" ? body.description : "ممیزی کامل سایت";

    if (!requestId || requestId.length > 128) {
      return response({ error: "request_id الزامی و حداکثر ۱۲۸ کاراکتر است." }, 400);
    }
    if (!validUrl(target)) {
      return response({ error: "فقط URL معتبر HTTPS مجاز است." }, 400);
    }
    if (mode === "pre_contract" && access) {
      return response({ error: "در حالت قبل از قرارداد نباید دسترسی فعال باشد." }, 400);
    }
    if (language !== "fa") {
      return response({ error: "زبان گزارش این Gateway باید فارسی باشد." }, 400);
    }

    const upstream = new URL("/execute/website-audit", env.MANAGER_API_URL);
    const executionId = crypto.randomUUID();
    const upstreamResponse = await fetch(upstream, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": env.MANAGER_API_KEY,
        "x-execution-id": executionId,
      },
      body: JSON.stringify({
        request_id: requestId,
        url: target,
        mode,
        access,
        language,
        description,
      }),
    });

    if (!upstreamResponse.ok) {
      return response({
        status: "trigger_failed",
        request_id: requestId,
        execution_id: executionId,
        error: "اجرای Agent در Manager با خطا مواجه شد.",
      }, 502);
    }

    let result: unknown;
    try {
      result = await upstreamResponse.json();
    } catch {
      result = null;
    }

    return response({
      status: "accepted",
      request_id: requestId,
      execution_id: executionId,
      result,
    }, 202);
  },
};
