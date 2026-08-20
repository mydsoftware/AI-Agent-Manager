# پل اجرای ChatGPT → AI Agent Manager

## هدف
هر پیام شامل «AI Agent Manager» باید به یک فرمان استاندارد Manager تبدیل شود. اجرای واقعی در GitHub Actions انجام می‌شود و نتیجه در `agent_results/` و Artifact ذخیره می‌شود.

## قرارداد درخواست
فایل JSON در `agent_requests/` باید شامل `agent`، `url` و `description` باشد.

## قرارداد نتیجه
نتیجه باید شامل `status`، `request_id`، `agent`، `url`، `report` و در صورت خطا `error` باشد.

## امنیت
کلیدهای API، رمز عبور و Secret نباید داخل درخواست یا چت ذخیره شوند. دسترسی‌ها باید از GitHub Secrets یا اتصال امن سرویس استفاده کنند.

## چرخه
ChatGPT → request JSON → GitHub Actions → Manager → result JSON → Artifact/Repository → ChatGPT result reader.
