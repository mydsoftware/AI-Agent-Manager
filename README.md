# AI-Agent-Manager

هسته مدیریت، برنامه‌ریزی و هماهنگی چندایجنتی به‌همراه داشبورد مدیریتی.

## هدف

Manager هسته کنترلی مجموعه‌ای از ایجنت‌های تخصصی هوش مصنوعی است. کاربر فقط درخواست را ثبت می‌کند؛ Manager درخواست را تحلیل، برنامه‌ریزی، route و اجرا می‌کند و نتیجه را برمی‌گرداند.

## داشبورد مدیریتی

داشبورد فارسی و RTL مستقیماً توسط Flask سرو می‌شود و از APIهای واقعی Manager استفاده می‌کند:

```text
کاربر
 ↓
Dashboard / HTTP API
 ↓
Session Runtime
 ↓
Manager Runtime
 ↓
Intent / Planner
 ↓
Task Graph / Executor
 ↓
Specialist Agents
 ↓
Model Router / LLM Gateway
 ↓
LM Studio / Local Models
 ↓
GitHub / CI / Build
 ↓
Report / Memory
```

## قابلیت‌های فعلی

- Registry ایجنت‌های تخصصی
- Research، Developer، QA و GitHub Agent
- Planner و Router با routing مبتنی بر capability
- Vision با capability=`vision`
- اجرای وابسته وظایف و Agentic Loop
- Repair/Recovery و حافظه موقت/پایدار SQLite
- Session پایدار و clarification/resume
- HTTP API و Dashboard RTL
- احراز هویت اختیاری API با `AI_AGENT_MANAGER_API_KEY`
- محدودیت اندازه Body و طول درخواست
- اتصال واقعی به GitHub REST API
- Gateway سازگار با OpenAI API برای مدل‌های محلی
- fallback مدل بر اساس capability
- Context compaction/truncation با بودجه پیش‌فرض ۱۲K
- CI خودکار با pytest و GitHub Actions

## بیلد خودکار اندروید

وقتی متن کاربر شامل Android، اندروید، APK، AAB یا اپلیکیشن موبایل باشد، Planner به‌صورت خودکار یک مرحله `android-build` به Task Graph اضافه می‌کند.

این ایجنت از دو Workflow اختصاصی همین Repository استفاده می‌کند:

1. `android-build-automated.yml` — موتور اصلی Gradle برای test، build، APK Debug، APK Release و AAB Release.
2. `android-build.yml` — موتور دوم مبتنی بر `sparkfabrik/android-build-action@v1.5.0` برای ساخت APK و تکمیل AAB/Release.

ترتیب خودکار:

```text
Prompt کاربر
 ↓
Planner
 ↓
Developer / Specialist Agents
 ↓
Android Build Agent
 ↓
Gradle Workflow
 ↓ اگر شکست خورد
Build Android App Action Workflow
 ↓
APK / AAB Artifacts
 ↓
Report
```

ایجنت وضعیت Workflow را از GitHub پیگیری می‌کند و فقط در صورت شکست موتور اول سراغ موتور دوم می‌رود.

برای استفاده مستقل از Repository دیگر:

```text
AI_AGENT_MANAGER_REPOSITORY=owner/repository
AI_AGENT_MANAGER_BUILD_BRANCH=feature/manager-core
AI_AGENT_MANAGER_BUILD_TIMEOUT=900
```

برای اجرای واقعی این مرحله، `GITHUB_TOKEN` باید دسترسی اجرای GitHub Actions روی Repository را داشته باشد.

## معماری

```text
User Prompt
  ↓
IntentRouter / IntentParser
  ↓
ManagerOrchestrator
  ↓
MultiAgentPlanner
  ↓
Task Graph
  ├── Research Agent
  ├── Developer Agent
  ├── Vision Agent
  ├── QA Agent
  ├── GitHub Agent
  ├── GitHub Project Agent
  └── Android Build Agent
             ↓
      GitHub Actions
       ├── Gradle Native
       └── Build Android App Action
```

## مدل‌های محلی

| قابلیت | مدل پیش‌فرض |
|---|---|
| Planner / General | `qwen3.5-9b` |
| Developer | `qwen3.5-9b` |
| Coder | `qwen2.5-coder-7b` |
| Researcher | `qwen3.5-9b` |
| Reviewer / Tester | `qwen2.5-coder-7b` |
| Vision | `qwen3-vl-4b-instruct` |
| Embedding | `text-embedding-nomic-embed-text-v1.5` |

Provider پیش‌فرض `LM Studio` و endpoint پیش‌فرض `http://127.0.0.1:1234/v1` است.

## اجرای محلی

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

برای اجرای داشبورد:

```bash
flask --app "api.http:create_default_app()" run --host 127.0.0.1 --port 8080
```

## APIهای اصلی

```text
GET  /api/health
GET  /api/agents
POST /api/agents/{name}/enable
POST /api/agents/{name}/disable
POST /api/run
POST /api/session/start
POST /api/session/{session_id}/answer
GET  /api/session/{session_id}
```

## تنظیمات محیطی

```text
AI_AGENT_MANAGER_API_KEY=...
AI_AGENT_MANAGER_MAX_REQUEST_LENGTH=12000
AI_AGENT_MANAGER_MAX_BODY_BYTES=1048576
AI_AGENT_MANAGER_REPOSITORY=mydsoftware/AI-Agent-Manager
AI_AGENT_MANAGER_BUILD_BRANCH=feature/manager-core
AI_AGENT_MANAGER_BUILD_TIMEOUT=900
LLM_CONTEXT_TOKENS=12288
LLM_CONTEXT_RESERVE_TOKENS=1024
LLM_TIMEOUT=120
LLM_MAX_RETRIES=2
```

## امنیت

- Secretها نباید در Repository قرار بگیرند.
- API Key و GitHub Token فقط از محیط اجرا خوانده می‌شوند.
- Session ID برای نام فایل sanitize می‌شود.
- ورودی API محدودیت طول و اندازه Body دارد.
- `main` نباید توسط Agent تغییر داده شود؛ عملیات توسعه باید روی branch کاری انجام شود.

## CI

Workflow اصلی `.github/workflows/ci.yml` است. Workflowهای Android فقط در صورت وجود پروژه معتبر `android/gradlew` موفق می‌شوند و Artifactهای APK/AAB را منتشر می‌کنند.

## قانون زبان پروژه

تمام READMEها، مستندات، توضیحات، راهنماها، کامنت‌های کد و پیام‌های کاربری پروژه باید فارسی باشند. نام متغیرها، کلاس‌ها، توابع، مسیر فایل‌ها و شناسه‌های فنی می‌توانند انگلیسی و استاندارد باقی بمانند.
