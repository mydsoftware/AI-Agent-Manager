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
      "X-GitHub-Api-Version": "2026-03-10",
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

function slugify(value: string): string {
  const slug = value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 45);
  return slug || "ai-project";
}

function encodeBase64(value: string): string {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function decodeBase64(value: string): string {
  const binary = atob(value.replace(/\s/g, ""));
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

function jsonFileContent(value: unknown): string {
  return JSON.stringify(value, null, 2) + "\n";
}

function parsePlan(value: string): Record<string, unknown> {
  if (!value?.trim()) throw new Error("plan_json الزامی است؛ ChatGPT باید قبل از اجرای Agent، Plan کامل پروژه را تولید کند.");
  let parsed: unknown;
  try {
    parsed = JSON.parse(value);
  } catch (error) {
    throw new Error(`plan_json نامعتبر است: ${String(error)}`);
  }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("plan_json باید یک شیء JSON باشد.");
  }
  const plan = parsed as Record<string, unknown>;
  if (!Array.isArray(plan.files) || !Array.isArray(plan.commands)) {
    throw new Error("Plan باید شامل آرایه‌های files و commands باشد.");
  }
  if (plan.done !== true) {
    throw new Error("Plan باید با done=true ارسال شود تا Agent چرخه کامل اجرا را آغاز کند.");
  }
  return plan;
}

function autonomousAgentRepository(env: Env): string {
  const configured = (env.AUTONOMOUS_AGENT_REPO || "").trim();
  if (!configured) return "mydsoftware/GitHub-Autonomous-Agent";
  return configured.includes("/") ? configured : `${env.GITHUB_OWNER}/${configured}`;
}

async function putContentFile(env: Env, repository: string, path: string, content: string, branch: string) {
  const payload: Record<string, string> = {
    message: `feat: initialize ${path}`,
    content: encodeBase64(content),
    branch,
  };
  try {
    const existing = await api(env, `/repos/${repository}/contents/${path}?ref=${encodeURIComponent(branch)}`);
    if (existing?.sha) payload.sha = existing.sha as string;
  } catch (error) {
    const message = String(error);
    if (!message.includes("GitHub API 404")) throw error;
  }
  return api(env, `/repos/${repository}/contents/${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function autonomousAgentWorkflow(env: Env): Promise<string> {
  const repository = autonomousAgentRepository(env);
  const data = await api(env, `/repos/${repository}/contents/.github/workflows/agent.yml?ref=main`);
  if (!data?.content) throw new Error("فایل Workflow عامل خودکار پیدا نشد.");
  return decodeBase64(data.content as string);
}

async function ensureAutonomousAgentWorkflow(env: Env, repository: string, branch: string) {
  const workflow = await autonomousAgentWorkflow(env);
  await putContentFile(env, repository, ".github/workflows/agent.yml", workflow, branch);
}

async function dispatchAutonomousAgent(
  env: Env,
  payload: { target_repository: string; target_branch: string; plan: Record<string, unknown> },
) {
  const [owner, repo] = payload.target_repository.split("/");
  if (!owner || !repo) throw new Error(`target_repository نامعتبر است: ${payload.target_repository}`);
  await ensureAutonomousAgentWorkflow(env, payload.target_repository, payload.target_branch);
  await api(env, `/repos/${owner}/${repo}/dispatches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_type: "ai-agent-project", client_payload: payload }),
  });
  return {
    repository: payload.target_repository,
    agent_source_repository: autonomousAgentRepository(env),
    event_type: "ai-agent-project",
    target_repository: payload.target_repository,
    target_branch: payload.target_branch,
    status: "dispatched-to-target-repository",
  };
}

async function createProjectRepository(
  env: Env,
  input: {
    name: string;
    description: string;
    private: boolean;
    request: string;
    projectType: string;
    planJson: string;
  },
) {
  const plan = parsePlan(input.planJson);
  const baseName = slugify(input.name);
  const name = `${baseName}-${Date.now().toString().slice(-6)}`;
  const repo = await api(env, "/user/repos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      description: input.description.slice(0, 350),
      private: input.private,
      auto_init: true,
      has_issues: true,
      has_projects: false,
      has_wiki: false,
      has_discussions: false,
    }),
  });

  const repository = repo.full_name as string;
  const branch = repo.default_branch || "main";
  const files: Record<string, string> = {
    "PROJECT_REQUEST.json": jsonFileContent({
      source: "AI-Agent-Manager",
      request: input.request,
      project_type: input.projectType,
      status: "agent-dispatched",
      language: "fa",
      direction: "rtl",
      created_at: new Date().toISOString(),
    }),
    "README.md": `# ${input.name}\n\n${input.description}\n\n## AI-Agent-Manager\n\nاین پروژه توسط AI-Agent-Manager ایجاد و برای اجرای کامل به عامل خودکار ارسال شده است.\n\n### درخواست اولیه\n\n${input.request}\n\n### استاندارد زبان\n\nتمام محتوای قابل مشاهده، مستندات، README، کامنت‌ها، پیام‌های تست و گزارش‌ها باید فارسی باشند؛ مواردی که استاندارد فنی الزام می‌کند انگلیسی بمانند.\n`,
    "agent/state.json": jsonFileContent({ status: "dispatched", phase: "build-test-security", next: "agent-execution", language: "fa", direction: "rtl" }),
  };

  for (const [path, content] of Object.entries(files)) {
    await putContentFile(env, repository, path, content, branch);
  }

  const execution = await dispatchAutonomousAgent(env, {
    target_repository: repository,
    target_branch: branch,
    plan: {
      ...plan,
      summary: plan.summary || input.request,
      done: true,
      language: "fa",
      direction: "rtl",
      localization: {
        required: true,
        language: "fa",
        direction: "rtl",
        comments: "fa",
        readme: "fa",
        documentation: "fa",
        ui: "fa",
        test_messages: "fa",
        reports: "fa",
        commit_messages: "fa",
      },
    },
  });

  return {
    repository,
    url: repo.html_url,
    clone_url: repo.clone_url,
    branch,
    project_type: input.projectType,
    status: "agent-dispatched",
    files: Object.keys(files),
    execution,
  };
}

function server(env: Env) {
  const mcp = new McpServer({ name: "AI-Agent-Manager Global MCP", version: "1.4.0" });

  mcp.tool(
    "create_project_repository",
    "ساخت Repository مستقل و اجرای اجباری چرخه کامل Agent. ChatGPT باید قبل از فراخوانی این ابزار Plan کامل JSON شامل files و commands و done=true تولید کند. هیچ اجرای صرفاً اسکلت اولیه پذیرفته نیست.",
    {
      name: z.string().min(1).max(80),
      description: z.string().min(1).max(350),
      request: z.string().min(1),
      project_type: z.enum(["html", "website", "web", "software", "wordpress", "python", "other"]).default("website"),
      private: z.boolean().default(true),
      plan_json: z.string().min(2).describe("Plan JSON کامل تولیدشده توسط ChatGPT؛ باید شامل files و commands و done=true باشد."),
    },
    async ({ name, description, request, project_type, private: isPrivate, plan_json }) => ({
      content: [{
        type: "text",
        text: JSON.stringify(await createProjectRepository(env, {
          name,
          description,
          request,
          projectType: project_type,
          private: isPrivate,
          planJson: plan_json,
        }), null, 2),
      }],
    }),
  );

  mcp.tool(
    "run_project_agent",
    "اجرای اجباری Plan ChatGPT روی یک Repository موجود؛ Plan باید کامل و دارای files، commands و done=true باشد.",
    {
      repository: z.string().regex(/^[^/]+\/[^/]+$/),
      branch: z.string().default("main"),
      plan_json: z.string().min(2).describe("Plan JSON کامل تولیدشده توسط ChatGPT"),
    },
    async ({ repository, branch, plan_json }) => {
      const plan = parsePlan(plan_json);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(await dispatchAutonomousAgent(env, {
            target_repository: repository,
            target_branch: branch,
            plan,
          }), null, 2),
        }],
      };
    },
  );

  mcp.tool(
    "submit_project_request",
    "ثبت درخواست عمومی پروژه در GitHub-Autonomous-Agent.",
    {
      request: z.string().min(1),
      repository: z.string().default("mydsoftware/GitHub-Autonomous-Agent"),
      branch: z.string().optional(),
      base: z.string().default("main"),
    },
    async ({ request, repository, branch, base }) => {
      const [owner, repo] = repository.split("/");
      const title = `ChatGPT Agent Request: ${request.slice(0, 80)}`;
      const body = JSON.stringify({ source: "ChatGPT Global MCP", done: true, request, repository, branch: branch || `ai-agent/chatgpt-${Date.now()}`, base }, null, 2);
      const issue = await api(env, `/repos/${owner}/${repo}/issues`, { method: "POST", body: JSON.stringify({ title, body }), headers: { "Content-Type": "application/json" } });
      return { content: [{ type: "text", text: JSON.stringify({ issue_url: issue.html_url, issue_number: issue.number, repository }, null, 2) }] };
    },
  );

  mcp.tool("get_project_request", "دریافت وضعیت یک درخواست ثبت‌شده در GitHub.", {
    repository: z.string(), issue_number: z.number().int(),
  }, async ({ repository, issue_number }) => {
    const [owner, repo] = repository.split("/");
    const issue = await api(env, `/repos/${owner}/${repo}/issues/${issue_number}`);
    return { content: [{ type: "text", text: JSON.stringify({ state: issue.state, title: issue.title, url: issue.html_url, body: issue.body }, null, 2) }] };
  });

  mcp.tool("get_repository", "بررسی سریع Repository مقصد و شاخه پیش‌فرض آن.", { repository: z.string() }, async ({ repository }) => {
    const [owner, repo] = repository.split("/");
    const data = await api(env, `/repos/${owner}/${repo}`);
    return { content: [{ type: "text", text: JSON.stringify({ full_name: data.full_name, default_branch: data.default_branch, private: data.private }, null, 2) }] };
  });

  return mcp;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") return new Response(JSON.stringify({ status: "ok", service: "AI-Agent-Manager Global MCP", version: "1.4.0" }), { headers: { "Content-Type": "application/json" } });
    if (url.pathname !== "/mcp") return new Response("AI-Agent-Manager Global MCP", { status: 200 });
    if (!authorized(request, env)) return new Response("Unauthorized", { status: 401 });
    const mcp = server(env);
    const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    await mcp.connect(transport);
    return transport.handleRequest(request);
  },
};
