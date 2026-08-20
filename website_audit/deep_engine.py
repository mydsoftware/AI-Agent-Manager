from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .advanced import analyze_browser, analyze_html
from .engine import WebsiteAuditEngine


class _CrawlerParser(HTMLParser):
    """لینک‌ها و منابع اصلی یک صفحه را بدون اجرای JavaScript استخراج می‌کند."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.images: list[tuple[str, str]] = []
        self.scripts = 0
        self.styles = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "a" and data.get("href"):
            self.links.append(data["href"] or "")
        elif tag == "img" and data.get("src"):
            self.images.append((data["src"] or "", data.get("alt") or ""))
        elif tag == "script":
            self.scripts += 1
        elif tag == "link" and (data.get("rel") or "").lower() == "stylesheet":
            self.styles += 1


class DeepWebsiteAuditEngine:
    """ممیزی چندصفحه‌ای با خزش، تحلیل HTML، عملکرد مرورگر و دسترس‌پذیری."""

    def __init__(self, timeout: int = 20, max_pages: int = 30) -> None:
        self.timeout = timeout
        self.max_pages = max_pages
        self.base = WebsiteAuditEngine(timeout=timeout)

    def audit(self, url: str, run_browser: bool = True):
        normalized = self.base._normalize_url(url)
        report = self.base.audit(normalized, run_browser=run_browser)
        origin = f"{urlparse(normalized).scheme}://{urlparse(normalized).netloc}"
        queue: deque[str] = deque([normalized])
        visited: set[str] = set()
        broken: list[str] = []
        pages: list[str] = []
        total_images = 0
        scripts = 0
        styles = 0

        while queue and len(visited) < self.max_pages:
            current = queue.popleft()
            if current in visited or urlparse(current).netloc != urlparse(normalized).netloc:
                continue
            visited.add(current)
            try:
                response = self._get(current)
                body = response.read(1_500_000).decode("utf-8", errors="replace")
                parser = _CrawlerParser()
                parser.feed(body)
                pages.append(current)
                total_images += len(parser.images)
                scripts += parser.scripts
                styles += parser.styles
                if current == normalized:
                    report.findings.extend(analyze_html(body))
                for href in parser.links:
                    target = urljoin(current, href).split("#", 1)[0]
                    parsed = urlparse(target)
                    if parsed.scheme in {"http", "https"} and parsed.netloc == urlparse(normalized).netloc:
                        if target not in visited and len(queue) + len(visited) < self.max_pages:
                            queue.append(target)
            except Exception:
                broken.append(current)

        robots = self._get_optional(f"{origin}/robots.txt")
        sitemap = self._get_optional(f"{origin}/sitemap.xml")
        if robots is None:
            report.findings.append(self.base._finding("خزش-001", "خزش و ایندکس", "فایل robots.txt قابل دریافت نیست", "متوسط", "robots.txt در مسیر استاندارد دریافت نشد.", "کنترل خزش موتورهای جستجو ممکن است ناقص باشد.", ["فایل robots.txt را در ریشه دامنه ایجاد و بررسی کنید."], True))
        if sitemap is None:
            report.findings.append(self.base._finding("خزش-002", "خزش و ایندکس", "نقشه سایت XML پیدا نشد", "زیاد", "sitemap.xml در مسیر استاندارد دریافت نشد.", "کشف و ایندکس صفحات برای موتور جستجو می‌تواند ضعیف‌تر شود.", ["یک XML Sitemap معتبر ایجاد کنید.", "آدرس Sitemap را در robots.txt و Search Console ثبت کنید."], True))
        if broken:
            report.findings.append(self.base._finding("لینک-001", "لینک‌ها", "صفحات داخلی قابل دریافت نیستند", "زیاد", f"حداقل {len(broken)} آدرس در فرایند خزش با خطا مواجه شد.", "کاربر و موتور جستجو ممکن است با صفحات خراب روبه‌رو شوند.", ["وضعیت HTTP هر آدرس را بررسی کنید.", "لینک خراب را اصلاح، ریدایرکت یا در صورت نیاز حذف کنید.", "پس از اصلاح دوباره خزش را اجرا کنید."], False))
        if len(pages) == 1 and self.max_pages > 1:
            report.findings.append(self.base._finding("خزش-003", "ساختار سایت", "خزش چندصفحه‌ای محدود شد", "کم", "فقط یک صفحه داخلی قابل کشف بود.", "ممیزی ساختار داخلی سایت کامل نیست.", ["منوی اصلی و لینک‌های داخلی را بررسی کنید تا صفحات مهم قابل کشف باشند."], False))

        if run_browser:
            self._run_advanced_browser(normalized, report)

        report.next_steps = [
            "ابتدا موارد بحرانی و با اهمیت زیاد را اصلاح کنید.",
            "برای اصلاحات خودکار، ابتدا نسخه پشتیبان و دسترسی محدود ایجاد کنید.",
            "برای داده‌های واقعی جستجو، اتصال Google Search Console را مرحله‌به‌مرحله فعال کنید.",
            "برای سنجش عملکرد قبل و بعد، اتصال PageSpeed Insights را فعال کنید.",
            "پس از هر دسته اصلاح، ممیزی را دوباره اجرا و نتیجه قبل/بعد را مقایسه کنید.",
        ] + report.next_steps
        report.summary += f" در خزش کنترل‌شده {len(pages)} صفحه، {total_images} تصویر، {scripts} اسکریپت و {styles} فایل CSS شناسایی شد."
        return report

    def _run_advanced_browser(self, url: str, report) -> None:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
                page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                report.findings.extend(analyze_browser(page))
                report.findings.extend(analyze_html(page.content()))
                browser.close()
        except Exception:
            # ممیزی پایه قبلاً وضعیت شکست Playwright را ثبت کرده است؛ اینجا خروجی را دوباره تکرار نمی‌کنیم.
            return

    def _get(self, url: str):
        request = Request(url, headers={"User-Agent": "AI-Agent-Manager-Website-Auditor/1.0"})
        return urlopen(request, timeout=self.timeout)

    def _get_optional(self, url: str) -> str | None:
        try:
            with self._get(url) as response:
                return response.read(500_000).decode("utf-8", errors="replace")
        except Exception:
            return None
