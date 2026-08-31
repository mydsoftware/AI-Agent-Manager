# Sandbox

## هدف
اجرای امن کد و شل تولیدشده.

## معماری
`Sandbox.run_python` / `run_shell` / `run_node`.

## تنظیمات
`SANDBOX_ENABLED`, `SANDBOX_BACKEND`, `SANDBOX_TIMEOUT_SECONDS`, `SANDBOX_NETWORK`

## مثال
```python
r = s.sandbox.run_python("print(1+1)")
assert r.success
```

## نکات امنیتی
شبکه پیش‌فرض خاموش؛ الگوهای مخرب مسدود.

## عیب‌یابی
بدون Docker از subprocess استفاده می‌شود.
