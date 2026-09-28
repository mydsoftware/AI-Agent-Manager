# موتور رشد کسب‌وکار

AI-Agent-Manager چرخه زیر را اجرا می‌کند:

```text
Strategy → Website → SEO → Content → Lead Generation
→ Marketing → Sales → Analytics → Optimization ↺
```

## اجرای واقعی

هر مرحله می‌تواند یک `GrowthAction` تولید کند. `GrowthActionRegistry` اقدام را
به Adapter متناظر تحویل می‌دهد. Adapter پیش‌فرض Dry Run است؛ بنابراین تا زمانی
که اتصال و credential واقعی تعریف نشده، Agent ادعای اجرای اقدام خارجی نمی‌کند.

Adapterهای قابل اتصال:

- Website/GitHub Engineering Loop
- Search Console
- Analytics
- CRM
- Lead Sources
- Marketing Channels
- Messaging
- Finance/Revenue

## KPI

- traffic
- organic_clicks
- leads
- qualified_leads
- conversion_rate
- customers
- revenue

## Target اولیه

`کارثبت / karsabt.ir`

بازار اولیه: دزفول

کانال اولیه Lead Generation: دیوار

هیچ credential، token یا اطلاعات خصوصی نباید در Repository ذخیره شود.
