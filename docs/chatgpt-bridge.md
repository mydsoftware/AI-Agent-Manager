# پل ChatGPT → AI-Agent-Manager

این پل درخواست را به‌صورت فایل JSON وارد صف `agent_requests/` می‌کند. GitHub Actions آن را اجرا می‌کند، Manager مسیر Agentها را ثبت می‌کند، DeepSeek فایل‌های پروژه را تولید می‌کند و GitHubAgent فایل‌ها را در Branch جدید می‌نویسد و Pull Request می‌سازد.

## قرارداد درخواست

```json
{
  "request": "یک سایت فروشگاهی با HTML بساز",
  "repository": "mydsoftware/demo-store",
  "base": "main",
  "branch": "ai-agent/demo-store",
  "pr_title": "ساخت سایت فروشگاهی با HTML"
}
```

## Secrets موردنیاز

- `DEEPSEEK_API_KEY`: کلید DeepSeek
- `GH_PAT`: در صورت کار روی Repository دیگری غیر از همین Repository، یک GitHub token با دسترسی لازم به Repository مقصد

اگر مقصد خود همین Repository باشد، `GITHUB_TOKEN` خود Actions کافی است.

## خروجی

نتیجه در `agent_results/<request-name>.json` ثبت می‌شود و Pull Request پروژه تولیدشده در خروجی Workflow اعلام می‌شود.
