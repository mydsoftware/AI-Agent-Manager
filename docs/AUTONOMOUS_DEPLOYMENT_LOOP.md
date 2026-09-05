# حلقه استقرار خودکار

مسیر استاندارد توسعه خودکار:

`CI → Preview → Browser QA → Analyze → Fix → Commit → Preview → QA`

قوانین:

1. اگر CI موفق نباشد، Preview اجرا نمی‌شود.
2. هر Preview باید URL معتبر برگرداند.
3. شکست Browser QA وارد تحلیل می‌شود.
4. اصلاح و Commit فقط با callbackهای صریح اجرا می‌شوند.
5. تعداد تلاش‌ها محدود است تا حلقه بی‌نهایت ایجاد نشود.
6. پس از QA موفق، وضعیت `production_pending_approval` تولید می‌شود.
7. این لایه خودش Production را deploy نمی‌کند؛ Production همچنان پشت Approval Gate می‌ماند.

این طراحی امکان اتصال بعدی به GitHub Actions، Vercel و Agent Executor را بدون دور زدن سیاست‌های امنیتی فراهم می‌کند.
