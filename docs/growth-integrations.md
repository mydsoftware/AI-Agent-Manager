# اتصال سرویس‌های Growth Engine

Growth Engine اطلاعات حساس را داخل repository ذخیره نمی‌کند.

## Environment Variables

### Search Console
- GROWTH_SEARCH_CONSOLE_PROPERTY

### Analytics
- GROWTH_ANALYTICS_PROPERTY

### CRM
- GROWTH_CRM_BASE_URL
- GROWTH_CRM_API_KEY

### WhatsApp
- GROWTH_WHATSAPP_BASE_URL
- GROWTH_WHATSAPP_API_KEY

### Lead Source
- GROWTH_LEAD_SOURCE_BASE_URL
- GROWTH_LEAD_SOURCE_API_KEY

## قرارداد Adapter

هر Provider باید این قرارداد را پیاده کند:

`execute(action: GrowthAction) -> dict`

Registry برای actionهایی که Provider ندارند Dry-Run اجرا می‌کند؛ بنابراین فعال‌سازی اتصال واقعی باید صریح و از طریق ثبت Adapter انجام شود.
