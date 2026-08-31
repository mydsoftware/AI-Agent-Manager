# Plugin Architecture

## هدف
افزودن tool/agent/provider بدون تغییر هسته.

## معماری
`plugin.json` + `PluginManager`.

## تنظیمات
`PLUGINS_ENABLED`, `PLUGINS_DIR`

## مثال
`plugins/sample_echo_tool/`

## نکات امنیتی
مجوز ناشناخته رد می‌شود.

## عیب‌یابی
`GET /platform/plugins`
