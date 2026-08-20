# Gateway اجرای AI Agent Manager

این Gateway برای اتصال امن کلاینت‌های بیرونی به API اجرای Manager طراحی شده است.

## قرارداد

`POST /execute/website-audit`

Headers:

- `Authorization: Bearer <GATEWAY_TOKEN>`
- `Content-Type: application/json`

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

Gateway باید درخواست را به Manager `/execute/website-audit` ارسال کند و `execution_id` و وضعیت را برگرداند.

## امنیت

- توکن Gateway فقط به‌صورت Secret نگهداری شود.
- URL داخلی Manager نباید در کلاینت عمومی افشا شود.
- درخواست‌های `pre_contract` نباید دسترسی مدیریتی دریافت کنند.
- لاگ‌ها نباید API key، توکن، Cookie یا اطلاعات احراز هویت مشتری را ذخیره کنند.
- برای جلوگیری از تکرار اجرا، `request_id` باید idempotent باشد.

## استقرار

Gateway می‌تواند به‌صورت Cloudflare Worker یا سرویس HTTPS معادل مستقر شود. Secretها باید از Secret Store پلتفرم خوانده شوند.
