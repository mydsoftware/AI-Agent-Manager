# Gateway اجرای AI Agent Manager

این Gateway مرز امن بین کلاینت و API داخلی Manager است.

## قرارداد

`POST /execute/website-audit`

Headers:

`Authorization: Bearer <GATEWAY_TOKEN>`

Body:

```json
{
  "request_id": "20260820-germantechsat",
  "url": "https://germantechsat.com",
  "mode": "pre_contract",
  "access": false,
  "language": "fa",
  "description": "ممیزی کامل سایت"
}
```

Gateway باید درخواست را اعتبارسنجی کند، Secret را هرگز در پاسخ یا Log چاپ نکند، و آن را به Manager داخلی ارسال کند.

## قرارداد پاسخ

```json
{
  "status": "accepted",
  "request_id": "...",
  "execution_id": "..."
}
```

نتیجه نهایی باید از مسیر امن نتیجه قابل دریافت باشد.

## اصل امنیتی

Gateway نباید API Key داخلی Manager را از کاربر بگیرد یا به کاربر برگرداند. Secret فقط از Secret Store/Environment خوانده می‌شود.
