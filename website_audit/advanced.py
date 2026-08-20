from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urlparse

from .models import AuditFinding


class _AdvancedParser(HTMLParser):
    """اطلاعات لازم برای دسترس‌پذیری و داده ساختاریافته را جمع‌آوری می‌کند."""

    def __init__(self) -> None:
        super().__init__()
        self.headings: list[str] = []
        self.buttons = 0
        self.inputs_without_label = 0
        self.iframes = 0
        self.json_ld = 0
        self.schema_types: list[str] = []
        self.lang = ""
        self._last_heading = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang") or ""
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._last_heading = tag
            self.headings.append(tag)
        elif tag == "button":
            self.buttons += 1
        elif tag == "iframe":
            self.iframes += 1
        elif tag == "input" and not (data.get("aria-label") or data.get("id")):
            self.inputs_without_label += 1
        elif tag == "script" and (data.get("type") or "").lower() == "application/ld+json":
            self.json_ld += 1

    def handle_data(self, data: str) -> None:
        if self._last_heading and data.strip():
            self._last_heading = ""


def analyze_html(content: str) -> list[AuditFinding]:
    parser = _AdvancedParser()
    parser.feed(content)
    findings: list[AuditFinding] = []

    if not parser.lang:
        findings.append(AuditFinding(
            id="دسترس‌پذیری-002", category="دسترس‌پذیری", title="زبان اصلی صفحه مشخص نشده است", severity="متوسط",
            evidence="ویژگی lang برای عنصر html پیدا نشد.", impact="صفحه‌خوان‌ها و برخی ابزارهای کمکی زبان محتوا را دقیق تشخیص نمی‌دهند.",
            solution=["ویژگی lang متناسب با زبان اصلی صفحه را روی html قرار دهید.", "برای صفحات فارسی از lang=fa استفاده کنید."], auto_fix=True,
        ))
    if parser.inputs_without_label:
        findings.append(AuditFinding(
            id="دسترس‌پذیری-003", category="دسترس‌پذیری", title="برخی ورودی‌های فرم برچسب قابل تشخیص ندارند", severity="زیاد",
            evidence=f"حداقل {parser.inputs_without_label} ورودی بدون label یا aria-label شناسایی شد.", impact="کاربران صفحه‌خوان ممکن است ندانند هر ورودی چه کاربردی دارد.",
            solution=["برای هر ورودی label مرتبط اضافه کنید.", "در موارد لازم aria-label یا aria-labelledby معتبر استفاده کنید.", "فرم را با صفحه‌خوان و کیبورد دوباره آزمایش کنید."], auto_fix=True,
        ))
    if parser.headings:
        levels = [int(item[1]) for item in parser.headings]
        if any(b - a > 1 for a, b in zip(levels, levels[1:])):
            findings.append(AuditFinding(
                id="دسترس‌پذیری-004", category="ساختار محتوا", title="ترتیب تیترها پرش دارد", severity="متوسط",
                evidence=f"سطوح تیتر مشاهده‌شده: {', '.join(parser.headings)}", impact="ساختار صفحه برای پیمایش سریع و ابزارهای کمکی مبهم می‌شود.",
                solution=["سطوح H2 تا H6 را بدون پرش و بر اساس ساختار واقعی محتوا مرتب کنید."], auto_fix=True,
            ))
    if parser.json_ld == 0:
        findings.append(AuditFinding(
            id="سئو-ساختاری-001", category="داده ساختاریافته", title="داده ساختاریافته JSON-LD پیدا نشد", severity="کم",
            evidence="script با نوع application/ld+json در HTML پیدا نشد.", impact="موتور جستجو ممکن است اطلاعات معنایی غنی کمتری از صفحه دریافت کند.",
            solution=["در صورت تناسب، Schema.org مرتبط با نوع صفحه را با JSON-LD اضافه کنید.", "داده ساختاریافته را با ابزار اعتبارسنجی Schema آزمایش کنید."], auto_fix=False,
        ))
    return findings


def analyze_browser(page) -> list[AuditFinding]:
    """شاخص‌های عملکرد و رفتار بصری را از صفحه واقعی مرورگر استخراج می‌کند."""
    findings: list[AuditFinding] = []
    metrics = page.evaluate("""() => ({
      fcp: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
      ttfb: performance.getEntriesByType('navigation')[0]?.responseStart || 0,
      domContentLoaded: performance.getEntriesByType('navigation')[0]?.domContentLoadedEventEnd || 0,
      resources: performance.getEntriesByType('resource').length,
      width: document.documentElement.scrollWidth,
      viewport: window.innerWidth
    })""")
    if metrics.get("fcp", 0) > 3000:
        findings.append(AuditFinding(
            id="عملکرد-002", category="عملکرد", title="نمایش نخستین محتوای صفحه کند است", severity="زیاد",
            evidence=f"FCP تقریبی: {metrics['fcp']:.0f} میلی‌ثانیه.", impact="کاربر مدت بیشتری صفحه را در حالت بارگذاری می‌بیند.",
            solution=["CSS و JavaScript مسدودکننده رندر را کاهش دهید.", "تصویر اصلی و فونت‌های حیاتی را بهینه کنید.", "پس از اصلاح، FCP را دوباره اندازه‌گیری کنید."], auto_fix=False,
        ))
    if metrics.get("ttfb", 0) > 800:
        findings.append(AuditFinding(
            id="عملکرد-003", category="عملکرد", title="زمان پاسخ اولیه سرور زیاد است", severity="متوسط",
            evidence=f"TTFB تقریبی: {metrics['ttfb']:.0f} میلی‌ثانیه.", impact="شروع دریافت محتوا برای کاربر و خزنده به تأخیر می‌افتد.",
            solution=["کش سمت سرور را بررسی کنید.", "پایگاه داده و درخواست‌های کند را بهینه کنید.", "در صورت نیاز CDN و بهینه‌سازی زیرساخت را بررسی کنید."], auto_fix=False,
        ))
    return findings
