# AI-Agent-Manager

هسته مدیریت، برنامه‌ریزی و هماهنگی چندایجنتی.

## هدف

Manager هسته کنترلی مجموعه‌ای از ایجنت‌های تخصصی هوش مصنوعی است. درخواست کاربر به وظایف قابل اجرا تبدیل می‌شود، وظایف بر اساس وابستگی مرتب می‌شوند، به ایجنت مناسب می‌رسند، خطاها مدیریت می‌شوند و نتیجه نهایی گزارش می‌شود.

## قابلیت‌های فعلی

- Registry ایجنت‌های تخصصی
- Research، Developer، QA و GitHub Agent
- Planner و Router با routing مبتنی بر capability
- مسیر Vision از طریق Developer با capability=`vision`
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
- Gateway سازگار با OpenAI API برای مدل‌های محلی
- fallback مدل بر اساس capability
- Context compaction/truncation با بودجه پیش‌فرض ۱۲K
- آزمون‌های خودکار با pytest و GitHub Actions

## معماری

```text
کاربر
  ↓
HTTP API / Python API
  ↓
Manager Runtime
  ↓
IntentRouter / Orchestrator
  ↓
MultiAgentPlanner
  ↓
Task Graph / Executor
  ↓
Router
  ↓
Specialist Agent
  ↓
ModelRouter
  ↓
LLMGateway
  ↓
LM Studio / OpenAI-compatible API
  ↓
Local Model
  ↓
Recovery / Memory / Report
```

## مدل‌های محلی

پیکربندی مرجع برای سخت‌افزار فعلی پروژه:

| قابلیت | مدل پیش‌فرض |
|---|---|
| Planner / General | `qwen3.5-9b` |
| Developer | `qwen3.5-9b` |
| Coder | `qwen2.5-coder-7b` |
| Researcher | `qwen3.5-9b` |
| Reviewer / Tester | `qwen2.5-coder-7b` |
| Vision | `qwen3-vl-4b-instruct` |
| Embedding | `text-embedding-nomic-embed-text-v1.5` |

Provider پیش‌فرض `LM Studio` و endpoint پیش‌فرض `http://127.0.0.1:1234/v1` است. مدل‌ها از طریق `ModelRouter` انتخاب می‌شوند و Agentها نباید نام مدل را hard-code کنند.

### Routing

`IntentRouter` ابتدا intent و capability را تشخیص می‌دهد و `MultiAgentPlanner` آن route را به Task تبدیل می‌کند. نمونه‌ها:

```text
«این کد را اصلاح کن»
→ developer + capability=coder
→ qwen2.5-coder-7b

«این اسکرین‌شات را بررسی کن»
→ developer + capability=vision
→ qwen3-vl-4b-instruct

«درباره معماری سیستم تحقیق کن»
→ research + capability=general
→ qwen3.5-9b
```

برای هر capability می‌توان با متغیرهای `LLM_MODEL_*` مدل را override کرد.

## مدیریت Context

تمام درخواست‌های LLM از `ContextManager` عبور می‌کنند. سقف عملیاتی پیش‌فرض `12288` token و reserve پیش‌فرض `1024` token است. در overflow، پیام‌های کم‌اهمیت حذف یا truncate می‌شوند و Gateway می‌تواند با context کاهش‌یافته retry کند.

تنظیمات اصلی:

```text
LLM_CONTEXT_TOKENS=12288
LLM_CONTEXT_RESERVE_TOKENS=1024
LLM_TIMEOUT=120
LLM_MAX_RETRIES=2
```

Gateway همچنین fallback عمومی و fallbackهای تخصصی Vision/Coder/General را پشتیبانی می‌کند.

## اجرای محلی

ابتدا Python 3.12 یا بالاتر را نصب کنید و سپس آزمون‌ها را اجرا کنید:

```bash
python -m pip install -r requirements.txt
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

در صورت حذف `agent`، routing خودکار فعال می‌شود.

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

## تست و CI

تست‌های Gateway، routing و planner بدون نیاز به LM Studio قابل اجرا هستند. Workflow اصلی CI با Python 3.12، وابستگی‌ها و Chromium اجرا شده و دستور اصلی آن `pytest -q` است. نتیجه CI باید برای هر commit/PR به‌صورت واقعی بررسی شود و صرف وجود workflow به معنی موفقیت CI نیست.

## قانون زبان پروژه

تمام READMEها، مستندات، توضیحات، راهنماها، کامنت‌های کد و پیام‌های کاربری پروژه باید فارسی باشند. نام متغیرها، کلاس‌ها، توابع، مسیر فایل‌ها و شناسه‌های فنی می‌توانند انگلیسی و استاندارد باقی بمانند.
