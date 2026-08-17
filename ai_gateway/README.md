# لایه AI Gateway

این ماژول اتصال `AI-Agent-Manager` به دو Gateway مستقل را فراهم می‌کند:

- **OmniRoute**: مسیر اصلی پیش‌فرض
- **FreeLLMAPI**: مسیر مستقل و پشتیبان

هیچ‌کدام داخل کد Agentها hard-code نشده‌اند و هر دو از API سازگار با OpenAI استفاده می‌کنند.

## تنظیمات

```env
OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=...
FREELLMAPI_BASE_URL=http://localhost:3001/v1
FREELLMAPI_API_KEY=...
AI_GATEWAY_ORDER=omniroute,freellmapi
```

برای اولویت معکوس:

```env
AI_GATEWAY_ORDER=freellmapi,omniroute
```

برای اجبار یک مسیر در یک درخواست، مقدار `preferred` را در `AIGateway.complete()` مشخص کنید.

## اصل معماری

Agentها فقط با `AIGateway` صحبت می‌کنند. Providerها و Gatewayها قابل تعویض هستند و وضعیت OmniRoute یا FreeLLMAPI وارد منطق تخصصی Agentها نمی‌شود.
