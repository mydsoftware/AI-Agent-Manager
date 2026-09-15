# وضعیت نهایی انتشار

## وضعیت فعلی

- شاخه کاری: `feature/manager-core`
- CI آخرین commit: سبز
- احراز هویت API: `X-API-Key` و `Authorization: Bearer`
- Session Runtime: فعال
- Agentic Engineering Loop: فعال
- Failure Analysis و Repair Loop: فعال
- GitHub CI monitoring: فعال
- Android Build Agent: فعال
- WordPress Factory pipeline: فعال
- main: نباید توسط Agent تغییر کند

## قانون حلقه مهندسی

در هر خطا این چرخه باید بدون توقف و بدون نیاز به تأیید کاربر اجرا شود:

```text
Detect Failure
→ Collect Logs
→ Analyze Root Cause
→ Apply Minimal Repair
→ Commit
→ Run CI
→ Verify Same Commit
→ Repeat Until Green
```

## معیار FINAL GREEN

نسخه فقط زمانی FINAL GREEN محسوب می‌شود که:

1. آخرین commit روی `feature/manager-core` باشد.
2. GitHub Actions همان commit را با `success` تأیید کند.
3. هیچ تست شناخته‌شده‌ای شکست‌خورده نباشد.
4. main تغییر نکرده باشد.
5. خطاهای CI با Repair Loop بسته شده باشند.

## نکته انتشار

PR #2 همچنان برای ادغام با `main` استفاده می‌شود. تا زمانی که کاربر صراحتاً درخواست Merge ندهد، Agent نباید آن را merge کند.
