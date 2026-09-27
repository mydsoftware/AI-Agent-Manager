---
name: myd-tool-loop-test
description: Minimal tool-loop diagnostic skill for Google AI Edge Gallery. Executes JavaScript through run_js and returns the computed result to the model.
---

# MYD Tool Loop Test

این Skill فقط برای تست حلقه Tool است.

## ابزار

از `run_js` با Script زیر استفاده کن:

- script name: `index.html`
- data: JSON string

## دستور

وقتی کاربر یک عبارت ریاضی برای محاسبه می‌دهد:

1. عبارت را به یک expression ساده JavaScript تبدیل کن.
2. حتماً `run_js` را فراخوانی کن.
3. منتظر Tool Result بمان.
4. نتیجه واقعی Tool را بخوان.
5. نتیجه را به کاربر اعلام کن.

**مهم:** فقط گفتن «run_js را صدا زدم» کافی نیست. باید نتیجه Tool را دریافت و از آن استفاده کنی.

## تست استاندارد

برای درخواست:

`125 * 37`

باید ابزار را با این data اجرا کنی:

```json
{"expression":"125 * 37"}
```

و پس از دریافت نتیجه ابزار، پاسخ نهایی باید شامل:

`4625`

باشد.

اگر Tool Result برنگشت، اعلام کن که اجرای Tool نتیجه‌ای برنگردانده است و عدد را از خودت حدس نزن.
