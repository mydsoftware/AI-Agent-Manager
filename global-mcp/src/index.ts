import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";

interface Env {
  GITHUB_TOKEN: string;
  MCP_ACCESS_TOKEN: string;
  GITHUB_OWNER: string;
  AUTONOMOUS_AGENT_REPO: string;
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const api = async (env: Env, path: string, init: RequestInit = {}) => {
  const response = await fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "X-GitHub-Api-Version": "2026-03-10",
      "User-Agent": "AI-Agent-Manager-Global-MCP",
      ...(init.headers || {}),
    },
  });
  const text = await response.text();
  let data: any = text;
  try { data = JSON.parse(text); } catch {}
  if (!response.ok) throw new Error(`GitHub API ${response.status}: ${text}`);
  return data;
};

function authorized(request: Request, env: Env) {
  return (request.headers.get("authorization") || "") === `Bearer ${env.MCP_ACCESS_TOKEN}`;
}

function slugify(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 45) || "ai-project";
}

function b64(value: string) {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function fromB64(value: string) {
  const binary = atob(value.replace(/\s/g, ""));
  return new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0)));
}

function parsePlan(value: string): Record<string, unknown> {
  if (!value?.trim()) throw new Error("plan_json الزامی است.");
  let plan: any;
  try { plan = JSON.parse(value); } catch (e) { throw new Error(`plan_json نامعتبر است: ${String(e)}`); }
  if (!plan || typeof plan !== "object" || Array.isArray(plan)) throw new Error("plan_json باید شیء JSON باشد.");
  if (!Array.isArray(plan.files) || !Array.isArray(plan.commands)) throw new Error("Plan باید شامل files و commands باشد.");
  if (plan.done !== true) throw new Error("Plan باید دارای done=true باشد.");
  return plan;
}

function agentRepo(env: Env) {
  const value = (env.AUTONOMOUS_AGENT_REPO || "").trim();
  return value ? (value.includes("/") ? value : `${env.GITHUB_OWNER}/${value}`) : "mydsoftware/GitHub-Autonomous-Agent";
}

async function putFile(env: Env, repository: string, path: string, content: string, branch: string) {
  const payload: any = { message: `feat: initialize ${path}`, content: b64(content), branch };
  try {
    const current = await api(env, `/repos/${repository}/contents/${path}?ref=${encodeURIComponent(branch)}`);
    if (current?.sha) payload.sha = current.sha;
  } catch (e) {
    if (!String(e).includes("GitHub API 404")) throw e;
  }
  return api(env, `/repos/${repository}/contents/${path}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
}

async function installWorkflow(env: Env, repository: string, branch: string) {
  const source = agentRepo(env);
  const data = await api(env, `/repos/${source}/contents/.github/workflows/agent.yml?ref=main`);
  if (!data?.content) throw new Error("Workflow عامل خودکار پیدا نشد.");
  await putFile(env, repository, ".github/workflows/agent.yml", fromB64(data.content), branch);
}

async function waitForWorkflowActive(env: Env, repository: string) {
  const workflowPath = ".github/workflows/agent.yml";
  for (let attempt = 1; attempt <= 12; attempt++) {
    try {
      const workflow = await api(env, `/repos/${repository}/actions/workflows/${encodeURIComponent(workflowPath)}`);
      if (workflow?.state === "active") return workflow;
    } catch {}
    await sleep(1000);
  }
  throw new Error("Workflow عامل پس از ایجاد Repository فعال نشد.");
}

async function workflowRuns(env: Env, repository: string) {
  return api(env, `/repos/${repository}/actions/workflows/${encodeURIComponent("agent.yml")}/runs?per_page=10`);
}

async function dispatchWithConfirmation(env: Env, repository: string, branch: string, plan: Record<string, unknown>) {
  const [owner, repo] = repository.split("/");
  if (!owner || !repo) throw new Error(`target_repository نامعتبر است: ${repository}`);

  await installWorkflow(env, repository, branch);
  await waitForWorkflowActive(env, repository);

  const marker = Date.now();
  const body = JSON.stringify({ event_type: "ai-agent-project", client_payload: { target_repository: repository, target_branch: branch, plan } });
  let dispatched = 0;

  for (let attempt = 1; attempt <= 3; attempt++) {
    await api(env, `/repos/${owner}/${repo}/dispatches`, { method: "POST", headers: { "Content-Type": "application/json" }, body });
    dispatched++;
    for (let check = 1; check <= 8; check++) {
      await sleep(1000);
      const runs = await workflowRuns(env, repository);
      const run = (runs.workflow_runs || []).find((item: any) => new Date(item.created_at).getTime() >= marker - 2000);
      if (run) {
        return { status: "agent-started", workflow_run_id: run.id, workflow_run_url: run.html_url, attempts: dispatched };
      }
    }
  }
  throw new Error(`repository_dispatch ارسال شد اما پس از ${dispatched} تلاش هیچ اجرای جدیدی برای agent.yml ایجاد نشد.`);
}

async function createProjectRepository(env: Env, input: { name: string; description: string; private: boolean; request: string; projectType: string; planJson: string }) {
  const plan = parsePlan(input.planJson);
  const name = `${slugify(input.name)}-${Date.now().toString().slice(-6)}`;
  const repo = await api(env, "/user/repos", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, description: input.description.slice(0, 350), private: input.private, auto_init: true, has_issues: true, has_projects: false, has_wiki: false, has_discussions: false }) });
  const repository = repo.full_name as string;
  const branch = repo.default_branch || "main";

  await putFile(env, repository, "PROJECT_REQUEST.json", JSON.stringify({ source: "AI-Agent-Manager", request: input.request, project_type: input.projectType, status: "agent-dispatched", language: "fa", direction: "rtl", created_at: new Date().toISOString() }, null, 2) + "\n", branch);
  await putFile(env, repository, "README.md", `# ${input.name}\n\n${input.description}\n\n## AI-Agent-Manager\n\nاین پروژه برای اجرای کامل به عامل خودکار ارسال شده است.\n\n### استاندارد زبان\n\nتمام محتوای محصول، مستندات، README، کامنت‌ها، پیام‌های تست، گزارش‌ها و پیام‌های Commit باید فارسی باشند؛ مواردی که استاندارد فنی الزام می‌کند انگلیسی بمانند.\n`, branch);
  await putFile(env, repository, "agent/state.json", JSON.stringify({ status: "dispatching", phase: "build-test-security", language: "fa", direction: "rtl" }, null, 2) + "\n", branch);

  const execution = await dispatchWithConfirmation(env, repository, branch, { ...plan, summary: plan.summary || input.request, done: true, language: "fa", direction: "rtl", localization: { required: true, language: "fa", direction: "rtl", comments: "fa", readme: "fa", documentation: "fa", ui: "fa", test_messages: "fa", reports: "fa", commit_messages: "fa" } });
  return { repository, url: repo.html_url, branch, project_type: input.projectType, status: execution.status, execution };
}

function server(env: Env) {
  const mcp = new McpServer({ name: "AI-Agent-Manager Global MCP", version: "1.5.0" });
  mcp.tool("create_project_repository", "ساخت Repository و اجرای قطعی عامل خودکار پس از فعال‌شدن Workflow.", {
    name: z.string().min(1).max(80), description: z.string().min(1).max(350), request: z.string().min(1), project_type: z.enum(["html", "website", "web", "software", "wordpress", "python", "other"]).default("website"), private: z.boolean().default(true), plan_json: z.string().min(2),
  }, async ({ name, description, request, project_type, private: isPrivate, plan_json }) => ({ content: [{ type: "text", text: JSON.stringify(await createProjectRepository(env, { name, description, request, projectType: project_type, private: isPrivate, planJson: plan_json }), null, 2) }] }));

  mcp.tool("run_project_agent", "اجرای Plan کامل روی Repository موجود با تأیید شروع Workflow.", { repository: z.string().regex(/^[^/]+\/[^/]+$/), branch: z.string().default("main"), plan_json: z.string().min(2) }, async ({ repository, branch, plan_json }) => ({ content: [{ type: "text", text: JSON.stringify(await dispatchWithConfirmation(env, repository, branch, parsePlan(plan_json)), null, 2) }] }));

  mcp.tool("submit_project_request", "ثبت درخواست پروژه در GitHub.", { request: z.string().min(1), repository: z.string().default("mydsoftware/GitHub-Autonomous-Agent"), branch: z.string().optional(), base: z.string().default("main") }, async ({ request, repository, branch, base }) => {
    const [owner, repo] = repository.split("/");
    const issue = await api(env, `/repos/${owner}/${repo}/issues`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: `ChatGPT Agent Request: ${request.slice(0, 80)}`, body: JSON.stringify({ source: "ChatGPT Global MCP", done: true, request, repository, branch: branch || `ai-agent/chatgpt-${Date.now()}`, base }, null, 2) }) });
    return { content: [{ type: "text", text: JSON.stringify({ issue_url: issue.html_url, issue_number: issue.number, repository }, null, 2) }] };
  });

  mcp.tool("get_project_request", "دریافت وضعیت درخواست GitHub.", { repository: z.string(), issue_number: z.number().int() }, async ({ repository, issue_number }) => { const [owner, repo] = repository.split("/"); const issue = await api(env, `/repos/${owner}/${repo}/issues/${issue_number}`); return { content: [{ type: "text", text: JSON.stringify({ state: issue.state, title: issue.title, url: issue.html_url, body: issue.body }, null, 2) }] }; });
  mcp.tool("get_repository", "بررسی Repository و شاخه پیش‌فرض.", { repository: z.string() }, async ({ repository }) => { const [owner, repo] = repository.split("/"); const data = await api(env, `/repos/${owner}/${repo}`); return { content: [{ type: "text", text: JSON.stringify({ full_name: data.full_name, default_branch: data.default_branch, private: data.private }, null, 2) }] }; });
  return mcp;
}

export default { async fetch(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  if (url.pathname === "/health") return new Response(JSON.stringify({ status: "ok", service: "AI-Agent-Manager Global MCP", version: "1.5.0" }), { headers: { "Content-Type": "application/json" } });
  if (url.pathname !== "/mcp") return new Response("AI-Agent-Manager Global MCP", { status: 200 });
  if (!authorized(request, env)) return new Response("Unauthorized", { status: 401 });
  const mcp = server(env);
  const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  await mcp.connect(transport);
  return transport.handleRequest(request);
} };