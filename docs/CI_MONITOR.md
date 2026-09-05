# CI Monitor

مانیتور CI وضعیت GitHub Actions را برای یک Branch بررسی می‌کند.

## جریان

`GitHub Actions → CIMonitor → Failure Context → Agent → Fix → Commit → CI`

### اطلاعات Failure Context

- workflow
- run id
- branch و commit
- Jobهای شکست‌خورده
- حداکثر ۲۰٬۰۰۰ کاراکتر از لاگ هر Job

Token هرگز در Context یا خروجی Agent قرار نمی‌گیرد.

## محدودیت امنیتی

این سرویس فقط وضعیت و لاگ را می‌خواند. عملیات Commit/Push/Production باید از مسیرهای مجاز و Approval Policy پروژه عبور کنند.
