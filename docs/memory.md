# Shared Memory & RAG

## هدف
اشتراک زمینه پروژه بین ایجنت‌ها با ذخیره پایدار محلی.

## معماری
`SharedMemory` + `HashingEmbedding` + `ContextManager`. بک‌اند پیش‌فرض SQLite.

## تنظیمات
`MEMORY_ENABLED`, `MEMORY_BACKEND`, `MEMORY_PATH`

## مثال
```python
from core.bootstrap import build_services
s = build_services()
s.memory.add("shop", "requirement", "cart", "سبد خرید")
print(s.context.for_agent("shop", "developer", "cart"))
```

## نکات امنیتی
جستجوی حافظه API باید پشت API key باشد.

## عیب‌یابی
بدون Chroma سیستم به SQLite برمی‌گردد.
