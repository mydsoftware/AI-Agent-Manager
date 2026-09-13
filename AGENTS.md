# AGENTS.md — AI-Agent-Manager

## هدف
این مخزن یک Manager چندایجنتی برای اجرای خودکار درخواست کاربر است. هدف این راهنما این است که OpenCode + Qwen3.5 9B بتوانند پروژه را از وضعیت فعلی تا Production بدون تغییر تصادفی معماری جلو ببرند.

## محیط مدل محلی
- Provider اصلی: LM Studio
- API: `http://127.0.0.1:1234/v1`
- مدل عمومی/Planner/Research: `qwen3.5-9b`
- مدل Coding/Review/Test: `qwen2.5-coder-7b`
- مدل Vision: `qwen3-vl-4b-instruct`
- Embedding: `text-embedding-nomic-embed-text-v1.5`
- Context عملیاتی هدف روی لپ‌تاپ: حدود 12K token؛ از ارسال promptهای بزرگ‌تر از ظرفیت واقعی جلوگیری کن.

## قانون اصلی اجرا
1. هرگز مستقیم روی `main` توسعه نده.
2. branch کاری فعلی `feature/manager-core` است؛ قبل از تغییر، وضعیت branch و diff را بررسی کن.
3. تغییرات را کوچک، قابل تست و قابل بازگشت نگه دار.
4. قبل از ایجاد abstraction جدید، معماری و فایل‌های موجود را بخوان.
5. اگر requirement مبهم نیست، سؤال نپرس و تا رسیدن به نتیجه قابل تست ادامه بده.
6. هیچ secret، API key، token یا credential را commit نکن.
7. برای تغییرات معماری، تست regression اضافه کن.

## معماری فعلی
```text
User Request
  -> ManagerRuntime
  -> Orchestrator
  -> TaskExecutor
  -> AgenticLoop
  -> Router / ModelRouter
  -> Specialist Agent
  -> Tool / GitHub / عملیات
  -> Memory / PersistentMemory
  -> ManagerReport

LLM path:
Agent -> LLMGateway -> OpenAI-compatible API -> LM Studio -> Local Model
```

## Model Routing
Routing باید capability-based باشد، نه صرفاً نام Agent.

| Capability | Default model |
|---|---|
| planner | qwen3.5-9b |
| developer | qwen3.5-9b |
| coder | qwen2.5-coder-7b |
| researcher | qwen3.5-9b |
| reviewer | qwen2.5-coder-7b |
| tester | qwen2.5-coder-7b |
| vision | qwen3-vl-4b-instruct |
| embedding | text-embedding-nomic-embed-text-v1.5 |

Environment overrides باید حفظ شوند: `LLM_MODEL_*` و `LLM_MODEL`.

## Context Manager
هر درخواست LLM باید قبل از ارسال از Context Manager عبور کند.

الزامات:
- محاسبه تقریبی token budget قبل از request.
- سقف پیش‌فرض عملیاتی: 12288 token.
- اولویت حفظ: system instructions > current task > relevant tool output > recent history > قدیمی‌ترین history.
- در overflow، ابتدا history کم‌اهمیت compact شود؛ سپس tool outputهای غیرمرتبط truncate شوند.
- اگر هنوز جا کافی نیست، request با یک context کوچک‌تر retry شود؛ retry نباید prompt را بی‌نهایت بزرگ کند.
- پیام خطای واضح برای context overflow تولید شود.
- context policy باید مستقل از Provider باشد تا بعداً Ollama/سرویس دیگر نیز قابل استفاده باشد.

## LLMGateway
Gateway مسئول این موارد است:
- OpenAI-compatible chat completions
- timeout
- retry محدود
- استخراج پاسخ استاندارد
- health check
- ثبت latency، success/failure و usage

Gateway نباید منطق routing یا orchestration را داخل خود داشته باشد.

## Agentها
Agent تخصصی باید:
1. Task را دریافت کند.
2. capability مناسب را تعیین/اعلام کند.
3. model را از ModelRouter بگیرد.
4. prompt حداقلی و هدفمند بسازد.
5. نتیجه قابل استفاده برای Agent بعدی برگرداند.
6. failure را silent نکند.

## Sprint بعدی — Intelligent Routing + Context + E2E
این sprint باید حداقل این خروجی‌ها را داشته باشد:
- Intent/task classification
- capability-aware model routing
- Context Manager با budget حدود 12K
- compaction/truncation و recovery واقعی
- logging مدل، latency و usage
- اتصال امن Developer / Research / QA به Gateway
- unit tests بدون نیاز به LM Studio
- integration/E2E test اختیاری وقتی LM Studio در دسترس است
- تست regression برای مسیرهای قبلی

## تست
حداقل قبل از تحویل:
```powershell
pytest -q
```

اگر پروژه command دیگری برای lint/typecheck دارد، آن را نیز اجرا کن.

برای مسیرهای Node/Frontend موجود، build پروژه مربوطه را نیز اجرا کن.

اگر LM Studio در دسترس است، health و یک inference واقعی با `qwen3.5-9b` را تست کن؛ اگر در دسترس نیست، تست‌های mock نباید شکست بخورند.

## Git
Commitها کوتاه و معنی‌دار باشند، ترجیحاً Conventional Commits:
- `feat:` قابلیت جدید
- `fix:` اصلاح خطا
- `test:` تست
- `refactor:` بازطراحی بدون تغییر رفتار
- `docs:` مستندات

قبل از commit:
- diff را بررسی کن.
- فایل‌های ناخواسته را حذف کن.
- تست‌ها را اجرا کن.
- secretها را بررسی کن.

## Definition of Done
کار زمانی تمام است که:
- requirement پیاده‌سازی شده باشد؛
- تست‌های مربوطه سبز باشند؛
- regression قابل قبول باشد؛
- context overflow مسیر اصلی را خراب نکند؛
- routing مدل deterministic و قابل override باشد؛
- لاگ‌های ضروری موجود باشند؛
- مستندات مرتبط به‌روز باشند؛
- هیچ تغییر مستقیم روی `main` انجام نشده باشد.

## سبک توسعه برای OpenCode + Qwen3.5
- ابتدا inspect، سپس plan کوتاه، سپس implement.
- از بازنویسی گسترده فایل‌های سالم خودداری کن.
- dependency جدید فقط در صورت ضرورت واقعی اضافه شود.
- برای هر bug ابتدا reproduction/test بنویس.
- خطاهای build/test را خودت تا رسیدن به وضعیت سبز repair کن.
- در پایان خلاصه تغییرات، تست‌های اجراشده و موارد باقی‌مانده را گزارش کن.

## زبان
مستندات و گزارش‌های پروژه ترجیحاً فارسی باشند؛ نام فایل‌ها، APIها، کلاس‌ها و کد طبق convention انگلیسی باقی بماند.
