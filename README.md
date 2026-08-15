# AI-Agent-Manager

هسته مدیریت، برنامه‌ریزی و هماهنگی چندایجنتی.

## هدف

Manager هسته کنترلی مجموعه‌ای از ایجنت‌های تخصصی هوش مصنوعی است. درخواست کاربر به وظایف قابل اجرا تبدیل می‌شود، وظایف بر اساس وابستگی مرتب می‌شوند، به ایجنت مناسب می‌رسند، خطاها مدیریت می‌شوند و نتیجه نهایی گزارش می‌شود.

## قابلیت‌های فعلی

- Registry ایجنت‌های تخصصی
- Research، Developer، QA و GitHub Agent
- Planner و Router
- اجرای وابسته وظایف
- وضعیت‌های استاندارد Task
- Agentic Loop
- تلاش مجدد خودکار هنگام خطا
- حافظه موقت و حافظه پایدار SQLite
- گزارش ساختاریافته اجرای Manager
- API داخلی Python
- HTTP API با مسیرهای `/health` و `/execute`
- احراز هویت API با کلید محیطی
- اتصال واقعی به GitHub REST API
- ایجاد و به‌روزرسانی فایل‌های GitHub
- آزمون‌های خودکار با pytest و GitHub Actions

## معماری

```text
کاربر
  ↓
HTTP API / Python API
  ↓
Manager Runtime
  ↓
Planner
  ↓
Task Graph / Executor
  ↓
Router
  ↓
Agent تخصصی
  ↓
Tool / GitHub / عملیات واقعی
  ↓
Recovery
  ↓
Memory
  ↓
Report
  ↓
نتیجه
```

## اجرای محلی

ابتدا Python 3.12 یا بالاتر را نصب کنید و سپس آزمون‌ها را اجرا کنید:

```bash
python -m pip install pytest
python -m pytest -q
```

برای اجرای HTTP API:

```bash
python http_api.py
```

سرویس به‌صورت پیش‌فرض روی `127.0.0.1:8080` اجرا می‌شود.

### بررسی سلامت

```text
GET /health
```

### اجرای Manager

```text
POST /execute
X-API-Key: کلید شما
Content-Type: application/json
```

```json
{
  "request": "درخواست کاربر",
  "agent": "developer"
}
```

## تنظیم کلید API

کلید API در متغیر محیطی `AI_AGENT_MANAGER_API_KEY` قرار می‌گیرد.

## اتصال GitHub

برای عملیات واقعی GitHub، متغیر محیطی `GITHUB_TOKEN` را فقط در محیط اجرا تنظیم کنید. این مقدار نباید در Repository ذخیره یا Commit شود.

ایجنت GitHub از دستور JSON ساختاریافته پشتیبانی می‌کند. نمونه خواندن فایل:

```json
{
  "action": "file",
  "repository": "mydsoftware/AI-Agent-Manager",
  "path": "README.md",
  "ref": "feature/manager-core"
}
```

نمونه ایجاد یا به‌روزرسانی فایل:

```json
{
  "action": "put_file",
  "repository": "mydsoftware/AI-Agent-Manager",
  "path": "example.txt",
  "content": "متن فایل",
  "branch": "feature/manager-core",
  "message": "feat: به‌روزرسانی فایل"
}
```

## امنیت

- اطلاعات محرمانه نباید در کد یا Repository قرار بگیرند.
- کلید API فقط از محیط اجرا خوانده می‌شود.
- کلیدها با مقایسه امن بررسی می‌شوند.
- توکن GitHub فقط از محیط اجرا خوانده می‌شود.

## قانون زبان پروژه

تمام READMEها، مستندات، توضیحات، راهنماها، کامنت‌های کد و پیام‌های کاربری پروژه باید فارسی باشند. نام متغیرها، کلاس‌ها، توابع، مسیر فایل‌ها و شناسه‌های فنی می‌توانند انگلیسی و استاندارد باقی بمانند.
