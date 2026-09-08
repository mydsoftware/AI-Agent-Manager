# CI Monitor

مانیتور CI وضعیت GitHub Actions را برای یک Branch بررسی می‌کند.

## جریان

`GitHub Actions → CIMonitor → Failure Context → Agent → Fix → Commit → CI`

### اطلاعات Failure Context

- workflow
- run id
- branch و commit
- Jobهای شکست‌خورده
- حداکثر ۴٬۰۰۰ کاراکتر از لاگ هر Job
- حداکثر ۵ Job شکست‌خورده

لاگ‌ها پیش از ارسال excerpt به Agent با الگوهای شناخته‌شده Secret/Token پاک‌سازی می‌شوند؛ این پاک‌سازی تضمین‌کننده حذف هر نوع Credential ناشناخته نیست.

## محدودیت امنیتی

این سرویس فقط وضعیت و لاگ را می‌خواند. عملیات Commit/Push/Production باید از مسیرهای مجاز و Approval Policy پروژه عبور کنند.
