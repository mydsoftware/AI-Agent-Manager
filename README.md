# AI-Agent-Manager

هسته مدیریت، برنامه‌ریزی، اجرای چندایجنتی و رشد کسب‌وکار.

## Business Growth Engine

Manager می‌تواند درخواست‌های رشد کسب‌وکار را به چرخه اجرایی زیر تبدیل کند:

```text
Business Strategy
      ↓
Website Builder
      ↓
SEO
      ↓
Content
      ↓
Lead Generation
      ↓
Marketing
      ↓
Sales
      ↓
Analytics
      ↓
Growth Optimizer
      ↺
```

هر مرحله context مرحله قبل را دریافت می‌کند. مرحله Website Builder یک `engineering_plan` تولید می‌کند و Runtime آن را به `GitHub Project Agent` می‌سپارد تا از مسیر Engineering Loop اجرا، CI، review، security و در صورت نیاز repair انجام شود.

### Target اولیه

```text
کارثبت / karsabt.ir
```

خدمات هدف:
- ثبت شرکت
- پروانه و جواز کسب
- مجوز مشاغل خانگی
- کافی‌نت آنلاین
- خدمات اداری و سامانه‌ای

بازار اولیه: دزفول

ورودی اولیه Lead Generation: دیوار

### تنظیم Repository کسب‌وکار

```text
BUSINESS_GROWTH_REPOSITORY=mydsoftware/karsabt
BUSINESS_GROWTH_BRANCH=feature/website-foundation
```

این متغیرها فقط مقصد اجرای پروژه کسب‌وکار را مشخص می‌کنند و نباید شامل Token یا Secret باشند.

## معماری

```text
User Prompt
  ↓
Intent Router
  ↓
Business Growth Runtime
  ↓
Specialist Agents
  ↓
Website Engineering Plan
  ↓
GitHub Project Agent
  ↓
Engineering Loop
  ↓
CI / Review / Security / Repair
  ↓
SEO → Content → Leads → Marketing → Sales → Analytics
```
