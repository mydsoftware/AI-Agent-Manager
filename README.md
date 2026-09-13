# AI-Agent-Manager

هسته مدیریت، برنامه‌ریزی و هماهنگی چندایجنتی به‌همراه داشبورد مدیریتی.

## هدف

Manager هسته کنترلی مجموعه‌ای از ایجنت‌های تخصصی هوش مصنوعی است. کاربر از داشبورد درخواست را ثبت می‌کند؛ Manager درخواست را تحلیل، برنامه‌ریزی، route و اجرا می‌کند و نتیجه را برمی‌گرداند.

## داشبورد مدیریتی

داشبورد فارسی و RTL مستقیماً توسط Flask سرو می‌شود و از APIهای واقعی Manager استفاده می‌کند:

```text
Browser Dashboard
  ↓ REST API
Session / Run / Agent API
  ↓
Manager Runtime
  ↓
Planner → Router → Executor → Agents
  ↓
LLM Gateway → LM Studio → Local Models
```

قابلیت‌های داشبورد:
- نمای کلی وضعیت API و Agentها
- اجرای درخواست با Auto Routing
- Session و clarification/resume
- کنترل فعال/غیرفعال‌سازی Agentها
- Activity و آخرین خروجی
- رابط responsive و فارسی RTL
- تنظیم API Key در Session Storage مرورگر برای APIهای محافظت‌شده

پس از اجرای Flask، داشبورد از مسیر `/` یا `/dashboard` قابل دسترسی است.

## قابلیت‌های فعلی

- Registry ایجنت‌های تخصصی
- Research، Developer، QA و GitHub Agent
- Planner و Router با routing مبتنی بر capability
- مسیر Vision از طریق Developer با capability=`vision`
- اجرای وابسته وظایف
- Agentic Loop و Repair/Recovery
- حافظه موقت و حافظه پایدار SQLite
- Session پایدار و clarification/resume
- HTTP API و Dashboard API
- احراز هویت اختیاری API با `AI_AGENT_MANAGER_API_KEY`
- محدودیت اندازه Body و طول درخواست
- اتصال واقعی به GitHub REST API
- Gateway سازگار با OpenAI API برای مدل‌های محلی
- fallback مدل بر اساس capability
- Context compaction/truncation با بودجه پیش‌فرض ۱۲K
- آزمون‌های خودکار با pytest و GitHub Actions

## معماری

```text
کاربر
  ↓
Dashboard / HTTP API / Python API
  ↓
Session Runtime
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

برای اجرای داشبورد مدیریتی با Flask، می‌توان App Factory را مستقیماً توسط WSGI اجرا کرد:

```python
from api.http import create_default_app

app = create_default_app()
```

یا در محیط توسعه با Flask:

```bash
flask --app "api.http:create_default_app()" run --host 127.0.0.1 --port 8080
```

پس از اجرا:

```text
http://127.0.0.1:8080/
```

### APIهای اصلی

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

### احراز هویت

اگر `AI_AGENT_MANAGER_API_KEY` تنظیم شده باشد، APIهای مدیریتی به Header زیر نیاز دارند:

```text
X-API-Key: کلید شما
```

Health عمومی باقی می‌ماند و داشبورد از بخش «تنظیمات» امکان وارد کردن کلید را دارد. کلید در `sessionStorage` مرورگر ذخیره می‌شود و داخل Repository قرار نمی‌گیرد.

### تنظیمات محیطی

```text
AI_AGENT_MANAGER_API_KEY=...
AI_AGENT_MANAGER_MAX_REQUEST_LENGTH=12000
AI_AGENT_MANAGER_MAX_BODY_BYTES=1048576
LLM_CONTEXT_TOKENS=12288
LLM_CONTEXT_RESERVE_TOKENS=1024
LLM_TIMEOUT=120
LLM_MAX_RETRIES=2
```

## امنیت

- Secretها نباید در Repository قرار بگیرند.
- API Key فقط از محیط اجرا خوانده می‌شود.
- مقایسه کلید با مقایسه ثابت‌زمان انجام می‌شود.
- GitHub Token فقط از محیط اجرا خوانده می‌شود.
- Session ID برای نام فایل sanitize می‌شود.
- ورودی API محدودیت طول و اندازه Body دارد.

## CI

Workflow اصلی `.github/workflows/ci.yml` است و تست‌های پروژه را با Python 3.12 و Playwright اجرا می‌کند. صرف وجود Workflow به معنی موفقیت CI نیست؛ وضعیت واقعی Run باید از GitHub بررسی شود.

## قانون زبان پروژه

تمام READMEها، مستندات، توضیحات، راهنماها، کامنت‌های کد و پیام‌های کاربری پروژه باید فارسی باشند. نام متغیرها، کلاس‌ها، توابع، مسیر فایل‌ها و شناسه‌های فنی می‌توانند انگلیسی و استاندارد باقی بمانند.
