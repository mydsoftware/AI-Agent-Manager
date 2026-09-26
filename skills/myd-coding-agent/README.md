# MYD Coding Agent Skill

Skill اختصاصی برای Google AI Edge Gallery و Gemma 4.

این Skill مدل را به یک Agent متمرکز بر GitHub تبدیل می‌کند و امکان خواندن Repository، فایل‌ها، جستجوی کد، Issue، Pull Request و Commit را از طریق GitHub API فراهم می‌کند.

## نصب در AI Edge Gallery

1. پوشه `myd-coding-agent` را روی گوشی کپی کنید.
2. AI Edge Gallery → Agent Skills → Skills → + → Import local skill
3. پوشه را انتخاب کنید.
4. Skill را فعال کنید.
5. هنگام اولین اجرای Skill، GitHub Personal Access Token را وارد کنید.

برای استفاده از Repositoryهای public، بعضی عملیات بدون Token نیز ممکن است؛ ولی برای rate limit و private repository بهتر است Token داشته باشید.

## وضعیت فعلی

نسخه اول فقط READ است:
- Repository
- File
- Code Search
- Issues
- Pull Requests
- Commits

اجرای shell، Python، npm و تغییر مستقیم فایل‌های local گوشی در این Skill انجام نمی‌شود.

## معماری

Gemma 4 E2B IT
→ Agent Skills
→ MYD Coding Agent
→ GitHub API
→ Evidence
→ Plan / Observe / Repair / Report
