# پل ChatGPT → AI-Agent-Manager

مدل خارجی در این معماری استفاده نمی‌شود. **ChatGPT تنها کنترل‌کننده هوش مصنوعی است** و AI-Agent-Manager نقش Orchestrator/Executor را دارد.

درخواست‌ها به‌صورت ساختاریافته وارد `agent_requests/` می‌شوند و GitHub Actions آن‌ها را برای اجرای Manager پردازش می‌کند.

## قرارداد درخواست

```json
{
  "request": "یک سایت فروشگاهی با HTML بساز",
  "repository": "mydsoftware/demo-store",
  "base": "main",
  "branch": "ai-agent/demo-store"
}
```

## Secrets موردنیاز

- `GH_PAT`: فقط اگر Manager باید روی Repository دیگری با سطح دسترسی بیشتر کار کند.
- برای مدل هوش مصنوعی هیچ API Key خارجی لازم نیست.

## معماری

ChatGPT → GitHub → AI-Agent-Manager → Agents → GitHub → Tests → Result
