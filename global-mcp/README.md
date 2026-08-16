# Global ChatGPT MCP

این سرویس، پل سراسری ChatGPT به AI-Agent-Manager و GitHub-Autonomous-Agent است.

پس از یک‌بار اتصال MCP به ChatGPT، ابزارها در Conversationهای بعدی نیز قابل استفاده هستند؛ اجرای واقعی همچنان در GitHub انجام می‌شود.

## ابزارها

- `submit_project_request`: ارسال درخواست پروژه از ChatGPT به GitHub-Autonomous-Agent
- `get_project_request`: بررسی وضعیت درخواست
- `get_repository`: بررسی Repository مقصد

## معماری

```text
هر ChatGPT Chat
      ↓
Global MCP
      ↓
GitHub-Autonomous-Agent
      ↓
AI-Agent-Manager
      ↓
Build → Test → Security → Fix → Retest → Deploy
```

## Secrets Cloudflare

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `MCP_ACCESS_TOKEN`
- `GH_PAT`

`GH_PAT` باید دسترسی لازم برای Repositoryهای هدف را داشته باشد.

## اتصال به ChatGPT

بعد از Deploy، آدرس زیر را به عنوان Remote MCP server در تنظیمات ChatGPT اضافه کنید:

```text
https://<worker-domain>/mcp
```

هدر احراز هویت:

```text
Authorization: Bearer <MCP_ACCESS_TOKEN>
```

توکن را در چت عمومی ارسال نکنید.
