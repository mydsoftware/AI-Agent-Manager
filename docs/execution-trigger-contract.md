# قرارداد Trigger اجرای AI Agent Manager

## هدف
ایجاد یک قرارداد مستقل برای اجرای درخواست‌های Agent بدون وابستگی به Push فایل.

## جریان پیشنهادی
Client/ChatGPT → Execution Gateway → GitHub Actions workflow_dispatch → Manager → Result Store → Result Reader.

## ورودی
- request_id
- agent
- mode
- url
- access
- description

## خروجی
- status
- request_id
- agent
- url
- report
- limitations
- error

## امنیت
Gateway باید احراز هویت شود. Secretها هرگز در request JSON یا گزارش ذخیره نشوند. دسترسی‌های مشتری فقط از Secret/Connection امن خوانده شوند.

## رفتار خطا
اگر Trigger شکست خورد، وضعیت باید `trigger_failed` و خطای قابل‌تشخیص برگرداند. اگر Agent اجرا شد ولی ممیزی ناقص بود، وضعیت باید `completed_with_limitations` باشد؛ هرگز موفقیت کامل گزارش نشود.
