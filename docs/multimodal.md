# Multimodal Asset Pipeline

## هدف
تولید تصویر/صدا با Mock پیش‌فرض.

## معماری
`AssetManager` + `MockProvider`.

## تنظیمات
`MULTIMODAL_ENABLED`, `MULTIMODAL_OUTPUT_DIR`

## مثال
```python
from multimodal.pipeline import AssetRequest
s.assets.generate(AssetRequest(kind="image", prompt="coin", project_id="game"))
```

## نکات امنیتی
کلید سرویس پولی داخل کد نیست.

## عیب‌یابی
بدون کلید، Mock فایل می‌نویسد.
