import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";

interface Env {
  GITHUB_TOKEN: string;
  MCP_ACCESS_TOKEN: string;
  GITHUB_OWNER: string;
  AUTONOMOUS_AGENT_REPO: string;
}

const api = async (env: Env, path: string, init: RequestInit = {}) => {
  const response = await fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "AI-Agent-Manager-Global-MCP",
      ...(init.headers || {}),
    },
  });
  const text = await response.text();
  let data: unknown = text;
  try { data = JSON.parse(text); } catch {}
  if (!response.ok) throw new Error(`GitHub API ${response.status}: ${text}`);
  return data as any;
};

function authorized(request: Request, env: Env): boolean {
  const auth = request.headers.get("authorization") || "";
  return auth === `Bearer ${env.MCP_ACCESS_TOKEN}`;
}

function server(env: Env) {
  const mcp = new McpServer({ name: "AI-Agent-Manager Global", version: "1.0.0" });

  mcp.tool(
    "submit_project_request",
    "ارسال درخواست پروژه از ChatGPT به GitHub-Autonomous-Agent. Plan باید JSON معتبر باشد.",
    {
      request: z.string().min(1),
      repository: z.string().default("mydsoftware/GitHub-Autonomous-Agent"),
      branch: z.string().optional(),
      base: z.string().default("main"),
    },
    async ({ request, repository, branch, base }) => {
      const [owner, repo] = repository.split("/");
      const title = `ChatGPT Agent Request: ${request.slice(0, 80)}`;
      const body = JSON.stringify({
        source: "ChatGPT Global MCP",
        done: true,
        request,
        repository,
        branch: branch || `ai-agent/chatgpt-${Date.now()}`,
        base,
      }, null, 2);
      const issue = await api(env, `/repos/${owner}/${repo}/issues`, {
        method: "POST",
        body: JSON.stringify({ title, body }),
        headers: { "Content-Type": "application/json" },
      });
      return { content: [{ type: "text", text: JSON.stringify({ issue_url: issue.html_url, issue_number: issue.number, repository }, null, 2) }] };
    },
  );

  mcp.tool(
    "get_project_request",
    "دریافت وضعیت یک درخواست ثبت‌شده در GitHub.",
    { repository: z.string(), issue_number: z.number().int() },
    async ({ repository, issue_number }) => {
      const [owner, repo] = repository.split("/");
      const issue = await api(env, `/repos/${owner}/${repo}/issues/${issue_number}`);
      return { content: [{ type: "text", text: JSON.stringify({ state: issue.state, title: issue.title, url: issue.html_url, body: issue.body }, null, 2) }] };
    },
  );

  mcp.tool(
    "get_repository",
    "بررسی سریع Repository مقصد و شاخه پیش‌فرض آن.",
    { repository: z.string() },
    async ({ repository }) => {
      const [owner, repo] = repository.split("/");
      const data = await api(env, `/repos/${owner}/${repo}`);
      return { content: [{ type: "text", text: JSON.stringify({ full_name: data.full_name, default_branch: data.default_branch, private: data.private }, null, 2) }] };
    },
  );

  return mcp;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") return new Response(JSON.stringify({ status: "ok", service: "AI-Agent-Manager Global MCP" }), { headers: { "Content-Type": "application/json" } });
    if (url.pathname !== "/mcp") return new Response("AI-Agent-Manager Global MCP", { status: 200 });
    if (!authorized(request, env)) return new Response("Unauthorized", { status: 401 });

    const mcp = server(env);
    const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    await mcp.connect(transport);
    return transport.handleRequest(request);
  },
};
