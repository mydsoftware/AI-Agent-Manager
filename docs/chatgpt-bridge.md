# پل ChatGPT Free → AI-Agent-Manager

در این معماری **ChatGPT تنها کنترل‌کننده هوش مصنوعی است** و هیچ مدل خارجی مثل DeepSeek استفاده نمی‌شود.

از آنجا که پشتیبانی کامل MCP سفارشی در ChatGPT فعلاً برای Business/Enterprise/Edu ارائه می‌شود، مسیر عملی برای حساب Free این است که خود ChatGPT از اتصال GitHub استفاده کند و درخواست ساختاریافته را مستقیماً در Repository `AI-Agent-Manager` ثبت کند. GitHub Actions سپس Manager را اجرا می‌کند.

## جریان اجرا

```text
ChatGPT Free
  ↓
GitHub Connector
  ↓
AI-Agent-Manager / agent_requests
  ↓
GitHub Actions — ChatGPT → AI-Agent-Manager Bridge
  ↓
AI-Agent-Manager
  ↓
GitHub-Autonomous-Agent
  ↓
Build → Test → Security → Fix → Retest
  ↺
  ↓
Final Result
```

## قرارداد درخواست

هر درخواست یک فایل JSON در `agent_requests/` است:

```json
{
  "request": "یک سایت فروشگاهی با HTML بساز",
  "repository": "mydsoftware/demo-store",
  "base": "main",
  "branch": "ai-agent/demo-store",
  "project_type": "html",
  "private": true,
  "done": true
}
```

## رفتار ChatGPT

وقتی کاربر در هر چت درخواست پروژه بدهد، ChatGPT باید:

1. درخواست را به Plan قابل اجرا تبدیل کند.
2. Repository مقصد را مشخص کند یا در صورت نیاز Repository جدید بسازد.
3. یک `agent_requests/<unique-id>.json` در همین Repository ایجاد کند.
4. منتظر اجرای Workflow بماند.
5. نتیجه Build/Test/Security/Fix را از GitHub بررسی کند.
6. خروجی نهایی را به کاربر تحویل دهد.

بنابراین کاربر لازم نیست Workflow را دستی اجرا کند و نیازی به MCP یا API Key مدل خارجی ندارد.

## Secrets

- `GH_PAT`: فقط برای دسترسی Manager به Repositoryهای خصوصی مقصد، در صورت نیاز.
- `MCP_ACCESS_TOKEN`: فقط برای Remote MCP؛ مسیر Free به آن وابسته نیست.
- هیچ API Key برای DeepSeek یا مدل خارجی استفاده نمی‌شود.

## Workflow

`chat-manager-bridge.yml` با Push به `agent_requests/*.json` به‌صورت خودکار اجرا می‌شود.

## اصل مهم

Repository پروژه‌های واقعی می‌تواند Private بماند. فقط `AI-Agent-Manager` باید Public باشد تا GitHub-hosted Actions استاندارد آن رایگان بماند.
