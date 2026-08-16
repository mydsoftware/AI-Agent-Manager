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

function parsePlan(value: string | undefined): Record<string, unknown> | null {
  if (!value?.trim()) return null;
  const parsed = JSON.parse(value);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("plan_json باید یک شیء JSON باشد.");
  }
  return parsed as Record<string, unknown>;
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
    planJson?: string;
  },
) {
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
      status: "created",
      created_at: new Date().toISOString(),
    }),
    "README.md": `# ${input.name}\n\n${input.description}\n\n## AI-Agent-Manager\n\nاین پروژه توسط AI-Agent-Manager ایجاد شده است.\n\n### درخواست اولیه\n\n${input.request}\n`,
    "agent/state.json": jsonFileContent({ status: "created", phase: "planning", next: "build" }),
  };

  if (["html", "website", "web"].includes(input.projectType)) {
    files["site/index.html"] = `<!doctype html>\n<html lang="fa" dir="rtl">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>${input.name}</title>\n</head>\n<body>\n  <main>\n    <h1>${input.name}</h1>\n    <p>نسخه اولیه پروژه توسط AI-Agent-Manager ساخته شد.</p>\n  </main>\n</body>\n</html>\n`;
  }

  for (const [path, content] of Object.entries(files)) {
    await putContentFile(env, repository, path, content, branch);
  }

  let execution: Record<string, unknown> | null = null;
  const plan = parsePlan(input.planJson);
  if (plan) {
    execution = await dispatchAutonomousAgent(env, {
      target_repository: repository,
      target_branch: branch,
      plan: {
        ...plan,
        summary: plan.summary || input.request,
        done: plan.done ?? true,
      },
    });
  }

  return {
    repository,
    url: repo.html_url,
    clone_url: repo.clone_url,
    branch,
    project_type: input.projectType,
    status: execution ? "agent-dispatched" : "created",
    files: Object.keys(files),
    execution,
  };
}

function server(env: Env) {
  const mcp = new McpServer({ name: "AI-Agent-Manager Global MCP", version: "1.3.0" });

  mcp.tool(
    "create_project_repository",
    "ساخت Repository مستقل برای پروژه جدید، نصب Workflow عامل خودکار و در صورت ارائه Plan، اجرای آن داخل همان Repository.",
    {
      name: z.string().min(1).max(80),
      description: z.string().min(1).max(350),
      request: z.string().min(1),
      project_type: z.enum(["html", "website", "web", "software", "wordpress", "python", "other"]).default("website"),
      private: z.boolean().default(true),
      plan_json: z.string().optional().describe("Plan JSON تولیدشده توسط ChatGPT شامل summary/files/commands/done"),
    },
    async ({ name, description, request, project_type, private: isPrivate, plan_json }) => ({
      content: [{
        type: "text",
        text: JSON.stringify(
          await createProjectRepository(env, {
            name,
            description,
            request,
            projectType: project_type,
            private: isPrivate,
            planJson: plan_json,
          }),
          null,
          2,
        ),
      }],
    }),
  );

  mcp.tool(
    "run_project_agent",
    "اجرای Plan ChatGPT روی یک Repository موجود؛ Workflow عامل خودکار در مقصد نصب و سپس repository_dispatch همان‌جا اجرا می‌شود.",
    {
      repository: z.string().regex(/^[^/]+\/[^/]+$/),
      branch: z.string().default("main"),
      plan_json: z.string().min(2).describe("Plan JSON تولیدشده توسط ChatGPT"),
    },
    async ({ repository, branch, plan_json }) => {
      const plan = parsePlan(plan_json);
      if (!plan) throw new Error("plan_json الزامی است.");
      return {
        content: [{
          type: "text",
          text: JSON.stringify(
            await dispatchAutonomousAgent(env, {
              target_repository: repository,
              target_branch: branch,
              plan,
            }),
            null,
            2,
          ),
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
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ issue_url: issue.html_url, issue_number: issue.number, repository }, null, 2),
        }],
      };
    },
  );

  mcp.tool(
    "get_project_request",
    "دریافت وضعیت یک درخواست ثبت‌شده در GitHub.",
    {
      repository: z.string(),
      issue_number: z.number().int(),
    },
    async ({ repository, issue_number }) => {
      const [owner, repo] = repository.split("/");
      const issue = await api(env, `/repos/${owner}/${repo}/issues/${issue_number}`);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ state: issue.state, title: issue.title, url: issue.html_url, body: issue.body }, null, 2),
        }],
      };
    },
  );

  mcp.tool(
    "get_repository",
    "بررسی سریع Repository مقصد و شاخه پیش‌فرض آن.",
    { repository: z.string() },
    async ({ repository }) => {
      const [owner, repo] = repository.split("/");
      const data = await api(env, `/repos/${owner}/${repo}`);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ full_name: data.full_name, default_branch: data.default_branch, private: data.private }, null, 2),
        }],
      };
    },
  );

  return mcp;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({ status: "ok", service: "AI-Agent-Manager Global MCP" }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    if (url.pathname !== "/mcp") return new Response("AI-Agent-Manager Global MCP", { status: 200 });
    if (!authorized(request, env)) return new Response("Unauthorized", { status: 401 });
    const mcp = server(env);
    const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    await mcp.connect(transport);
    return transport.handleRequest(request);
  },
};
