from __future__ import annotations

from .models import AccessRequest


def build_access_requests() -> list[AccessRequest]:
    """دسترسی‌های اختیاری را به صورت مرحله‌ای و قابل فهم برای کاربر تعریف می‌کند."""
    return [
        AccessRequest(
            service="Google Search Console",
            title="دسترسی کنسول جستجوی گوگل",
            reason="برای بررسی داده‌های واقعی جستجو، صفحات ایندکس‌شده، خطاهای ایندکس و عملکرد جستجو.",
            steps=[
                "وارد حساب گوگل شوید که مالک سایت است.",
                "در Google Search Console سایت را انتخاب کنید.",
                "بخش تنظیمات و مدیریت کاربران را باز کنید.",
                "دسترسی لازم را طبق راهنمای نمایش‌داده‌شده برای Manager ایجاد کنید.",
                "پس از انجام، به Manager برگردید و اتصال را آزمایش کنید.",
            ],
            url="https://search.google.com/search-console",
            credential_name="دسترسی Google Search Console",
        ),
        AccessRequest(
            service="PageSpeed Insights",
            title="کلید API برای سنجش عملکرد گوگل",
            reason="برای دریافت داده‌های عملکرد و مقایسه نتایج قبل و بعد از اصلاح.",
            steps=[
                "وارد Google Cloud Console شوید.",
                "یک پروژه انتخاب یا ایجاد کنید.",
                "PageSpeed Insights API را فعال کنید.",
                "یک API Key بسازید و فقط همان کلید را در بخش اتصال Manager وارد کنید.",
            ],
            url="https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com",
            credential_name="کلید API سرویس PageSpeed Insights",
        ),
        AccessRequest(
            service="WordPress REST API",
            title="دسترسی مدیریت وردپرس",
            reason="برای اصلاح خودکار موارد مجاز مانند عنوان‌ها، متادیتا، محتوا یا تنظیمات سایت در صورت پشتیبانی افزونه.",
            steps=[
                "در پیشخوان وردپرس وارد بخش کاربران شوید.",
                "برای Manager یک Application Password بسازید.",
                "نام کاربری و Application Password را در اتصال امن Manager ثبت کنید.",
                "پس از تست اتصال، فقط مجوزهای لازم را فعال نگه دارید.",
            ],
            url="https://wordpress.org/documentation/article/application-passwords/",
            credential_name="نام کاربری + Application Password وردپرس",
        ),
    ]
