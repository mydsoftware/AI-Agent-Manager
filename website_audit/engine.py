from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .access import build_access_requests
from .models import AuditFinding, AuditReport


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.h1 = 0
        self.meta_description = ""
        self.viewport = False
        self.images_without_alt = 0
        self.links: list[str] = []
        self.forms = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta":
            if data.get("name", "").lower() == "description":
                self.meta_description = data.get("content") or ""
            if data.get("name", "").lower() == "viewport":
                self.viewport = True
        elif tag == "img" and not (data.get("alt") or "").strip():
            self.images_without_alt += 1
        elif tag == "a" and data.get("href"):
            self.links.append(data["href"] or "")
        elif tag == "form":
            self.forms += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data.strip()


class WebsiteAuditEngine:
    """ممیزی پایه و قابل توسعه سایت؛ خروجی قابل نمایش همیشه فارسی است."""

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def audit(self, url: str, run_browser: bool = True) -> AuditReport:
        normalized = self._normalize_url(url)
        findings: list[AuditFinding] = []
        parser = _PageParser()
        status = 0
        content = ""
        headers: dict[str, str] = {}
        try:
            request = Request(normalized, headers={"User-Agent": "AI-Agent-Manager-Website-Auditor/1.0"})
            with urlopen(request, timeout=self.timeout) as response:
                status = int(response.status)
                headers = {key.lower(): value for key, value in response.headers.items()}
                content = response.read(2_500_000).decode("utf-8", errors="replace")
            parser.feed(content)
        except (HTTPError, URLError, TimeoutError) as error:
            findings.append(AuditFinding(
                id="فنی-001", category="دسترسی", title="صفحه اصلی قابل دریافت نیست", severity="بحرانی",
                evidence=f"دریافت صفحه با خطا مواجه شد: {error}", impact="ممیزی کامل صفحه و تجربه کاربر ممکن نیست.",
                solution=["بررسی وضعیت سرور و DNS", "بررسی گواهی HTTPS و ریدایرکت‌ها", "پس از رفع مشکل، ممیزی را دوباره اجرا کنید."],
                auto_fix=False, user_action=["دسترسی سرور یا هاست را بررسی کنید."], status="ناموفق"
            ))
            return AuditReport(normalized, 0, "صفحه اصلی قابل دریافت نبود؛ ابتدا مشکل دسترسی باید برطرف شود.", findings, build_access_requests(), ["رفع مشکل دسترسی", "اجرای دوباره ممیزی"])

        self._check_basic(parser, normalized, findings)
        self._check_headers(headers, findings)
        self._check_security(normalized, content, findings)
        self._check_resources(normalized, parser.links, findings)
        if run_browser:
            self._check_responsive_with_browser(normalized, findings)

        score = max(0, 100 - sum(self._severity_weight(item.severity) for item in findings))
        summary = f"صفحه اصلی با وضعیت HTTP {status} بررسی شد و {len(findings)} مورد قابل پیگیری شناسایی شد."
        return AuditReport(
            url=normalized,
            score=score,
            summary=summary,
            findings=findings,
            access_requests=build_access_requests(),
            next_steps=self._next_steps(findings),
            mode="ممیزی عمومی + آزمون مرورگر" if run_browser else "ممیزی عمومی",
        )

    def _check_basic(self, parser: _PageParser, url: str, findings: list[AuditFinding]) -> None:
        if not parser.title:
            findings.append(self._finding("سئو-001", "سئو", "عنوان صفحه وجود ندارد", "زیاد", "عنصر title در HTML پیدا نشد.", "عنوان مناسب برای موتور جستجو و کاربر وجود ندارد.", ["برای صفحه یک عنوان کوتاه و دقیق بنویسید.", "عنوان را با موضوع و هدف صفحه هماهنگ کنید."], True))
        elif not 20 <= len(parser.title) <= 65:
            findings.append(self._finding("سئو-002", "سئو", "طول عنوان صفحه مناسب نیست", "متوسط", f"طول عنوان {len(parser.title)} نویسه است.", "عنوان ممکن است در نتایج جستجو ناقص یا کم‌اثر نمایش داده شود.", ["عنوان را با حفظ کلمه کلیدی اصلی به حدود ۲۰ تا ۶۵ نویسه نزدیک کنید."], True))
        if not parser.meta_description:
            findings.append(self._finding("سئو-003", "سئو", "توضیحات متا وجود ندارد", "متوسط", "Meta Description پیدا نشد.", "کنترل مناسبی روی متن معرفی صفحه در نتایج جستجو ندارید.", ["یک توضیح دقیق و غیرتکراری برای صفحه بنویسید."], True))
        if parser.h1 == 0:
            findings.append(self._finding("سئو-004", "ساختار محتوا", "عنوان اصلی H1 وجود ندارد", "زیاد", "هیچ H1 در صفحه پیدا نشد.", "ساختار معنایی صفحه برای کاربر و موتور جستجو ضعیف می‌شود.", ["یک H1 یکتا و توصیفی برای موضوع اصلی صفحه اضافه کنید."], True))
        elif parser.h1 > 1:
            findings.append(self._finding("سئو-005", "ساختار محتوا", "صفحه چند H1 دارد", "متوسط", f"تعداد H1 برابر {parser.h1} است.", "اولویت موضوع اصلی صفحه مبهم می‌شود.", ["یک H1 اصلی نگه دارید و عنوان‌های بعدی را با H2/H3 سازمان‌دهی کنید."], True))
        if not parser.viewport:
            findings.append(self._finding("ریسپانسیو-001", "ریسپانسیو", "تنظیم viewport وجود ندارد", "زیاد", "متا viewport در صفحه پیدا نشد.", "نمایش موبایل می‌تواند نادرست باشد.", ["meta viewport استاندارد را به head اضافه کنید.", "صفحه را در عرض‌های مختلف دوباره آزمایش کنید."], True))
        if parser.images_without_alt:
            findings.append(self._finding("دسترس‌پذیری-001", "دسترس‌پذیری", "تصویر بدون متن جایگزین وجود دارد", "متوسط", f"حداقل {parser.images_without_alt} تصویر بدون alt شناسایی شد.", "کاربران صفحه‌خوان و درک معنایی تصاویر آسیب می‌بینند.", ["برای تصاویر معنادار alt توصیفی بنویسید.", "برای تصاویر صرفاً تزئینی alt خالی استفاده کنید."], True))

    def _check_headers(self, headers: dict[str, str], findings: list[AuditFinding]) -> None:
        if "content-security-policy" not in headers:
            findings.append(self._finding("امنیت-001", "امنیت", "Content-Security-Policy تنظیم نشده است", "متوسط", "هدر CSP در پاسخ پیدا نشد.", "سطح دفاع در برابر برخی حملات تزریق محتوا کاهش می‌یابد.", ["یک CSP متناسب با منابع واقعی سایت طراحی و مرحله‌ای فعال کنید.", "قبل از اجرای سخت‌گیرانه، گزارش‌گیری CSP را بررسی کنید."], False))
        if "strict-transport-security" not in headers:
            findings.append(self._finding("امنیت-002", "امنیت", "HSTS تنظیم نشده است", "کم", "هدر Strict-Transport-Security پیدا نشد.", "مرورگر اجبار کمتری برای استفاده از HTTPS دارد.", ["پس از اطمینان از HTTPS کامل، HSTS را روی دامنه فعال کنید."], False))

    def _check_security(self, url: str, content: str, findings: list[AuditFinding]) -> None:
        if url.startswith("https://") and re.search(r"(?:src|href)=[\"']http://", content, re.I):
            findings.append(self._finding("امنیت-003", "امنیت", "منبع ناامن در صفحه HTTPS پیدا شد", "زیاد", "یک یا چند منبع با HTTP در صفحه HTTPS مشاهده شد.", "ممکن است Mixed Content و خطاهای مرورگر ایجاد شود.", ["همه منابع را به HTTPS منتقل کنید.", "منابع قدیمی را از قالب یا افزونه‌ها اصلاح کنید."], True))

    def _check_resources(self, base: str, links: list[str], findings: list[AuditFinding]) -> None:
        parsed = urlparse(base)
        external = sum(1 for href in links if urlparse(urljoin(base, href)).netloc and urlparse(urljoin(base, href)).netloc != parsed.netloc)
        if external > 30:
            findings.append(self._finding("عملکرد-001", "عملکرد", "تعداد لینک‌های خارجی زیاد است", "کم", f"حدود {external} مقصد خارجی در صفحه پیدا شد.", "وابستگی‌های خارجی می‌توانند هزینه شبکه و ریسک نگهداری را افزایش دهند.", ["لینک‌های غیرضروری را حذف کنید.", "منابع خارجی حیاتی را کاهش یا بهینه کنید."], False))

    def _check_responsive_with_browser(self, url: str, findings: list[AuditFinding]) -> None:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                for width in (320, 375, 390, 430, 768, 1366):
                    page.set_viewport_size({"width": width, "height": 900})
                    page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                    overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
                    if overflow:
                        findings.append(self._finding(f"ریسپانسیو-{width}", "ریسپانسیو", f"در عرض {width}px سرریز افقی دیده شد", "زیاد", "عرض محتوای سند از عرض viewport بیشتر است.", "کاربر موبایل مجبور به پیمایش افقی می‌شود.", ["عنصر ایجادکننده overflow را شناسایی کنید.", "عرض‌های ثابت را به max-width و واحدهای نسبی تبدیل کنید.", "پس از اصلاح، همان viewport را دوباره آزمایش کنید."], False))
                browser.close()
        except Exception as error:
            findings.append(self._finding("ممیزی-001", "آزمون مرورگر", "آزمون کامل مرورگر اجرا نشد", "متوسط", f"اجرای Playwright کامل نشد: {error}", "نتایج ریسپانسیو و رفتار واقعی صفحه ناقص می‌ماند.", ["مرورگر Chromium موردنیاز Playwright را نصب کنید.", "آزمون را دوباره اجرا کنید."], False))

    @staticmethod
    def _finding(id_: str, category: str, title: str, severity: str, evidence: str, impact: str, solution: list[str], auto_fix: bool) -> AuditFinding:
        return AuditFinding(id_, category, title, severity, evidence, impact, solution, auto_fix)

    @staticmethod
    def _severity_weight(severity: str) -> int:
        return {"بحرانی": 25, "زیاد": 10, "متوسط": 5, "کم": 2}.get(severity, 0)

    @staticmethod
    def _normalize_url(url: str) -> str:
        value = url.strip()
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
        return value.rstrip("/")

    @staticmethod
    def _next_steps(findings: list[AuditFinding]) -> list[str]:
        if not findings:
            return ["سایت در ممیزی پایه مشکل قابل گزارش پیدا نکرد؛ داده‌های واقعی Search Console و عملکرد را برای تحلیل عمیق‌تر متصل کنید."]
        return [
            "ابتدا موارد بحرانی و زیاد را اصلاح کنید.",
            "برای هر مورد قابل اصلاح خودکار، در صورت اتصال مدیریت سایت، اجرای اصلاح را فعال کنید.",
            "پس از اصلاح، ممیزی مجدد اجرا و نتیجه قبل و بعد مقایسه شود.",
            "برای تحلیل جستجو و عملکرد واقعی، دسترسی‌های پیشنهادی را مرحله‌به‌مرحله متصل کنید.",
        ]
