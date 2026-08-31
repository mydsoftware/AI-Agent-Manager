# Circuit Breaker & Budget

## هدف
توقف حلقه‌های معیوب و مصرف بیش از حد توکن/هزینه/زمان.

## معماری
`CircuitBreaker` و `BudgetController`.

## تنظیمات
`CIRCUIT_BREAKER_ENABLED`, `DEFAULT_TOKEN_BUDGET`, `DAILY_GLOBAL_TOKEN_BUDGET`

## مثال
```python
s.budget.can_start(task.id)
s.budget.record_tokens(task.id, tokens=1200, provider="ollama")
```

## نکات امنیتی
اتمام بودجه باید تسک را متوقف کند.

## عیب‌یابی
`GET /platform/budget`
