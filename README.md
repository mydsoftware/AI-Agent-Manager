# AI-Agent-Manager

> هسته مدیریت، برنامه‌ریزی و هماهنگی چندایجنتی با قابلیت تولید خودکار نرم‌افزار و بازی

## هدف

AI-Agent-Manager یک پلتفرم **Autonomous Agentic Development** است که می‌تواند:

1. پروژه نرم‌افزاری بسازد و مدیریت کند
2. پروژه بازی از ایده تا Build نهایی تولید کند
3. خطاها را تشخیص و خودکار اصلاح کند
4. CI/CD و Deployment را مدیریت کند
5. از Providerهای LLM رایگان استفاده کند

---

## نصب

```bash
python -m pip install -r requirements.txt
```

## پیکربندی

فایل `.env.example` را کپی و تنظیم کنید:

```bash
cp .env.example .env
```

### تنظیمات AI Gateway

```env
# اولویت Providerها
AI_PROVIDER_PRIORITY=openrouter,freebuff,opencode,ollama

# OpenRouter (رایگان)
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openrouter/free

# Freebuff
FREEBUFF_API_KEY=your-key
FREEBUFF_BASE_URL=https://api.freebuff.com/v1

# OpenCode
OPENCODE_BASE_URL=http://localhost:3001/v1
OPENCODE_API_KEY=your-key

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### تنظیمات GitHub

```env
GITHUB_TOKEN=your-github-token
```

### تنظیمات Deployment

```env
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id
```

---

## معماری

```
USER
  ↓
API / UI
  ↓
Manager Runtime
  ↓
Intent Analysis → Decision Engine
  ↓
Orchestrator
  ↓
Planner → Task Graph
  ↓
Agent Router
  ↓
Specialized Agents
  ↓
Tool Registry
  ↓
AI Gateway → Providers (OpenRouter, Freebuff, OpenCode, Ollama)
  ↓
Execution → Test → Review → Correction Loop
  ↓
Supervisor → Dynamic Replanning
  ↓
Git → GitHub → CI → Deploy → Verify
  ↓
Final Report
```

---

## AI Gateway

لایه مستقل ارتباط با Providerهای LLM:

### Providerها

| Provider | نوع | توضیح |
|----------|------|--------|
| OpenRouter | Cloud | مدل‌های رایگان |
| Freebuff | Cloud | ارائه‌دهنده مستقل |
| OpenCode | Cloud | ادغام Coding |
| Ollama | Local | اجرای محلی |

### Failover خودکار

اگر Provider اول پاسخ ندهد، خودکار به Provider بعدی منتقل می‌شود:

```
OpenRouter → Rate Limit → Freebuff → Unavailable → OpenCode → Unavailable → Ollama
```

### مسیریابی مدل

مدل Agentها قابل تنظیم است:

```env
PLANNER_MODEL=gpt-4
DEVELOPER_MODEL=gpt-4
TESTER_MODEL=gpt-3.5-turbo
```

---

## Agentها

### Agentهای اصلی

| Agent | نقش |
|-------|------|
| Planner | برنامه‌ریزی وظایف |
| Developer | توسعه کد |
| Reviewer | بازبینی کد |
| QA | تضمین کیفیت |
| Researcher | تحقیق |
| GitHub | مدیریت GitHub |
| Security | بررسی امنیت |
| Deploy | استقرار |

### Agentهای Game Factory

| Agent | نقش |
|-------|------|
| Game Designer | طراحی بازی (GDD) |
| Game Developer | پیاده‌سازی بازی |
| Game Writer | نوشتن داستان |
| Game Asset | مدیریت Assetها |
| Game Level Designer | طراحی سطوح |
| Game AI | هوش مصنوعی دشمنان |
| Game UI | رابط کاربری |
| Game Audio | صدا و موسیقی |
| Game QA | تست بازی |
| Game Build | Build بازی |

---

## Tool Registry

ابزارهای استاندارد:

| Tool | مجوز | توضیح |
|------|------|--------|
| filesystem | READ, WRITE, DELETE | خواندن/نوشتن فایل |
| shell | EXECUTE | اجرای فرمان |
| git | GIT | عملیات Git |
| github | GITHUB | عملیات GitHub |
| test | EXECUTE | اجرای تست |
| build | EXECUTE | اجرای Build |
| deploy | DEPLOY | استقرار |
| python | EXECUTE | اجرای Python |
| browser | BROWSER | تست وب |
| logs | READ | مشاهده لاگ |

---

## Game Factory

سیستم تولید خودکار بازی:

### مراحل تولید

```
Idea → GDD → Story → Architecture → Art Direction → Assets
  → Code → Levels → AI → UI → Audio → Tests → Playtest
  → Fix → Build → Verify → Final Package
```

### پلتفرم‌ها

- Android (APK, AAB)
- Web (dist/)
- Windows (EXE)
- Linux (Binary)
- macOS

### موتورها

- Godot (پیش‌فرض 2D)
- Unity (3D متوسط)
- Unreal (3D سنگین)
- Phaser (Web)
- Three.js (Web 3D)

---

## API

### سلامت سیستم

```http
GET /health
```

### Providerها

```http
GET /providers
```

### مدل‌ها

```http
GET /models
```

### Agentها

```http
GET /agents
```

### اجرای درخواست

```http
POST /execute
Content-Type: application/json

{
  "request": "درخواست کاربر",
  "agent": "developer"
}
```

### اجرای Async

```http
POST /execute/async
Content-Type: application/json
X-Execution-ID: exec-123

{
  "request": "درخواست کاربر"
}
```

### ایجاد پروژه نرم‌افزاری

```http
POST /project/create
Content-Type: application/json

{
  "name": "نام پروژه",
  "description": "توضیحات",
  "request": "درخواست ساخت",
  "project_type": "website"
}
```

### ایجاد پروژه بازی

```http
POST /game/create
Content-Type: application/json

{
  "name": "نام بازی",
  "description": "توضیحات بازی",
  "genre": "platformer",
  "platform": "android"
}
```

### Session

```http
POST /session/start
POST /session/answer
GET /session/{id}
```

### مسیریابی

```http
POST /route
Content-Type: application/json

{
  "request": "درخواست کاربر"
}
```

---

## اجرای محلی

```bash
# اجرای HTTP API
python http_api.py

# اجرای Session API
python session_api.py
```

سرور به‌صورت پیش‌فرض روی `127.0.0.1:8080` اجرا می‌شود.

---

## تست‌ها

```bash
python -m pytest -q
```

---

## Platform Extensions

گسترش‌های زیرساختی پلتفرم:

### SharedMemory

حافظه مشترک با پشتیبانی از چند backend:

| Backend | توضیح |
|---------|--------|
| SQLite | پیش‌فرض، سبک |
| JSON | فایلی، ساده |
| Chroma | برداری، جستجوی معنایی |

### Safety

لایه امنیتی اجرای ایجنت‌ها:

| ماژول | توضیح |
|-------|--------|
| Sandbox | اجرای محدود در محیط امن |
| Circuit Breaker | قطع مدار در صورت خطا |
| Budget | کنترل هزینه و مصرف توکن |

### HITL (Human-in-the-Loop)

تأیید انسانی قبل از اقدامات حساس:

- ایجاد/ویرایش/حذف فایل
- اجرای فرمان خطرناک
- Push به branch اصلی
- Deployment

### Observability (Tracer)

ردیابی دقیق تمام عملیات اجرا با جزئیات کامل.

### Plugin System

سیستم پلاگین با قابلیت افزودن ابزار و agent جدید:

```
plugins/
  sample_echo_tool/
    plugin.json    # متادیتای پلاگین
    echo.py        # پیاده‌سازی
```

### Multimodal Pipeline

پردازش چندرسانه‌ای (متن، تصویر، صدا) با قابلیت افزودن Provider جدید.

### Agentهای جدید

| Agent | نقش |
|-------|------|
| Database | مدیریت پایگاه‌داده |
| Documentation | تولید مستندات |

---

## Agent Builder CLI

CLI تعاملی برای ساخت و مدیریت ایجنت‌ها:

```bash
# حالت تعاملی
python cli.py

# ساخت مستقیم
python cli.py create --type developer --description "ایجنت توسعه" --language python

# لیست ایجنت‌ها
python cli.py list
```

### قالب‌های ایجنت

- `templates/python_agent.py` — قالب پایه پایتون
- `templates/js_agent.js` — قالب پایه جاوااسکریپت

### GitHub Actions

- `agent-builder.yml` — ساخت ایجنت با push به شاخه
- `issue-agent-builder.yml` — ساخت ایجنت از طریق Issue

---

## Gold Market Site

سایت نمایش قیمت لحظه‌ای طلا، سکه و ارز با Next.js:

```
gold-market-site/
  app/
    page.tsx              # داشبورد اصلی
    market/[symbol]/page.tsx  # صفحه اختصاصی نماد
    api/prices/route.ts   # API قیمت لحظه‌ای
    api/history/route.ts  # API تاریخچه
    api/analysis/route.ts # API تحلیل هوشمند
```

منبع داده: TGJU (سایت اطلاع‌رسانی قیمت)

---

## ساختار پروژه

```
AI-Agent-Manager/
├── ai_gateway/          # دروازه هوش مصنوعی + Providerها
├── agents/              # Agentهای تخصصی (60+ فایل)
├── api/                 # API عمومی
├── asset_generation/    # تولید خودکار Asset
├── config/              # تنظیمات یکپارچه
├── core/
│   ├── hitl/            # تأیید انسانی
│   ├── memory/          # حافظه مشترک
│   ├── observability/   # ردیابی اجرا
│   ├── plugins/         # سیستم پلاگین
│   └── safety/          # امنیت اجرا
├── game/                # کارخانه بازی‌سازی
├── gold-market-site/    # سایت قیمت طلا
├── manager/             # هسته مدیریت (55+ فایل)
├── multimodal/          # پردازش چندرسانه‌ای
├── plugins/             # پلاگین‌ها
├── prompts/             # پرامپت ایجنت‌ها
├── templates/           # قالب ایجنت
├── tests/               # تست‌ها (150+ فایل)
├── tools/               # ابزارهای استاندارد
├── ui/                  # رابط وب
├── cli.py               # CLI تعاملی
├── http_api.py          # HTTP API Server
├── session_api.py       # Session API
└── agent_builder.py     # سازنده ایجنت
```

---

## امنیت

- Secretها فقط از محیط اجرا خوانده می‌شوند
- کلیدها با مقایسه امن بررسی می‌شوند
- توکن GitHub هرگز در Log چاپ نمی‌شود
- Path Traversal ممنوع
- فرمان‌های خطرناک مسدود
- Sandbox execution برای ایجنت‌ها
- Circuit Breaker در صورت تعداد زیاد خطا
- کنترل بودجه مصرف توکن

---

## قانون زبان پروژه

تمام READMEها، مستندات و توضیحات پروژه باید **فارسی** باشند. نام متغیرها، کلاس‌ها و توابع می‌توانند انگلیسی باشند.
