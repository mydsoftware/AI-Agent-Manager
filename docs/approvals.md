# Human-in-the-Loop

## هدف
توقف عملیات پرریسک تا تأیید انسان.

## معماری
`ApprovalGateway` + سطوح ریسک + audit log.

## تنظیمات
`HITL_ENABLED`, `HITL_EXPIRY_SECONDS`, `HITL_AUTO_APPROVE_LOW`

## مثال
```python
req = s.approvals.require("deploy", {"env": "prod"})
```

## نکات امنیتی
deploy و push به main همیشه نیاز به تأیید دارند.

## عیب‌یابی
`GET /platform/approvals`
