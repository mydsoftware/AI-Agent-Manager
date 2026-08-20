interface Env {
  GATEWAY_TOKEN: string;
  MANAGER_API_URL: string;
  MANAGER_API_KEY: string;
  RESULT_API_URL?: string;
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

function authError(request: Request, env: Env): Promise<Response> {
  return (async () => {
    const supplied = bearer(request);
    if (!supplied || !(await constantTimeEqual(supplied, env.GATEWAY_TOKEN))) {
      return response({ error: "دسترسی غیرمجاز است." }, 401);
    }
    return response({ error: "" }, 200);
  })();
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

    const protectedPath = url.pathname === "/execute/website-audit" || url.pathname.startsWith("/executions/");
    if (!protectedPath) return response({ error: "مسیر درخواست پیدا نشد." }, 404);
    if (request.method !== "POST" && !(url.pathname.startsWith("/executions/") && request.method === "GET")) {
      return response({ error: "روش درخواست مجاز نیست." }, 405);
    }

    const auth = await authError(request, env);
    if (auth.status !== 200) return auth;

    if (url.pathname.startsWith("/executions/") && request.method === "GET") {
      const executionId = url.pathname.slice("/executions/".length).trim();
      if (!/^[0-9a-f-]{36}$/i.test(executionId)) {
        return response({ error: "execution_id نامعتبر است." }, 400);
      }
      const resultBase = env.RESULT_API_URL || env.MANAGER_API_URL;
      try {
        const resultUrl = new URL(`/executions/${executionId}`, resultBase);
        const upstream = await fetch(resultUrl, {
          headers: { "x-api-key": env.MANAGER_API_KEY },
        });
        const payload = await upstream.text();
        return new Response(payload, {
          status: upstream.status,
          headers: jsonHeaders,
        });
      } catch {
        return response({ status: "pending", execution_id: executionId }, 202);
      }
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

    if (!requestId || requestId.length > 128) return response({ error: "request_id الزامی و حداکثر ۱۲۸ کاراکتر است." }, 400);
    if (!validUrl(target)) return response({ error: "فقط URL معتبر HTTPS مجاز است." }, 400);
    if (mode === "pre_contract" && access) return response({ error: "در حالت قبل از قرارداد نباید دسترسی فعال باشد." }, 400);
    if (language !== "fa") return response({ error: "زبان گزارش این Gateway باید فارسی باشد." }, 400);

    const executionId = crypto.randomUUID();
    const upstream = new URL("/execute/website-audit", env.MANAGER_API_URL);
    try {
      const upstreamResponse = await fetch(upstream, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": env.MANAGER_API_KEY,
          "x-execution-id": executionId,
        },
        body: JSON.stringify({ request_id: requestId, url: target, mode, access, language, description }),
      });
      if (!upstreamResponse.ok) {
        return response({ status: "trigger_failed", request_id: requestId, execution_id: executionId, error: "اجرای Agent در Manager با خطا مواجه شد." }, 502);
      }
    } catch {
      return response({ status: "trigger_failed", request_id: requestId, execution_id: executionId, error: "ارتباط با Manager برقرار نشد." }, 502);
    }

    return response({
      status: "accepted",
      request_id: requestId,
      execution_id: executionId,
      result_url: `/executions/${executionId}`,
    }, 202);
  },
};
