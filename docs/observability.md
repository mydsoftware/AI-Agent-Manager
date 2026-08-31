# Observability

## هدف
ردیابی تسک، ایجنت، توکن، خطا.

## معماری
`Tracer` روی SQLite.

## تنظیمات
`OBSERVABILITY_ENABLED`, `OBSERVABILITY_PATH`

## مثال
`GET /platform/traces/<task_id>`

## نکات امنیتی
مسیر data را commit نکنید.

## عیب‌یابی
مسیر جدا برای تست تنظیم کنید.
