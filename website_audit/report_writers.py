from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from agents.website_audit import AuditFinding, WebsiteAuditReport


def _domain_slug(url: str) -> str:
    host = urlparse(url if "://" in url else f"https://{url}").hostname or "site"
    return re.sub(r"[^a-zA-Z0-9.-]+", "-", host).strip("-").lower() or "site"


def _default_http_get(url: str):
    """واکشی ساده HTTP برای Crawl عمومی."""
    import urllib.request

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Agent-Manager-PublicSiteScanner/1.0 (+https://github.com/mydsoftware/AI-Agent-Manager)"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        text = body.decode(charset, errors="replace")

        class _Resp:
            status_code = getattr(response, "status", 200)
            headers = dict(response.headers.items())
            text = ""

        result = _Resp()
        result.status_code = getattr(response, "status", 200)
        result.headers = dict(response.headers.items())
        result.text = text
        return result


def _render_problems_file(
    *,
    url: str,
    report: WebsiteAuditReport,
    pages_scanned: int,
    mode: str,
    access: bool,
) -> str:
    lines = [
        f"# گزارش مشکلات سایت",
        "",
        f"- **آدرس:** {url}",
        f"- **حالت:** {mode}",
        f"- **دسترسی:** {'دارد' if access else 'ندارد'}",
        f"- **زبان:** فارسی",
        f"- **صفحات اسکن‌شده:** {pages_scanned}",
        f"- **تعداد یافته‌ها:** {len(report.findings)}",
        f"- **زمان تولید:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## فهرست مشکلات",
        "",
    ]
    if not report.findings:
        lines.append("مشکل قطعی و قابل گزارش از مشاهدات عمومی ثبت نشد.")
    else:
        for index, finding in enumerate(report.findings, start=1):
            lines.extend(
                [
                    f"### {index}. {finding.title}",
                    f"- **دسته:** {finding.category}",
                    f"- **شدت:** {finding.severity}",
                    f"- **تأثیر:** {finding.impact}",
                    f"- **شواهد:** {finding.evidence}",
                    f"- **نیاز به دسترسی:** {'بله' if finding.requires_access else 'خیر'}",
                    "",
                ]
            )
    if report.limitations:
        lines.append("## محدودیت‌های این گزارش")
        lines.append("")
        for item in report.limitations:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_solutions_file(
    *,
    url: str,
    report: WebsiteAuditReport,
    mode: str,
    access: bool,
) -> str:
    lines = [
        f"# راه‌های اصلاح مشکلات سایت",
        "",
        f"- **آدرس:** {url}",
        f"- **حالت:** {mode}",
        f"- **دسترسی:** {'دارد' if access else 'ندارد'}",
        "",
        "## راهنمای کلی",
        "",
    ]
    if access and mode == "post_contract":
        lines.append(
            "دسترسی اعلام شده است. موارد قابل‌اجرای خودکار در صورت اتصال ابزار Write اعمال می‌شوند؛ "
            "موارد باقی‌مانده را طبق مراحل دستی زیر انجام دهید."
        )
    else:
        lines.append(
            "فعلاً دسترسی مدیریتی برای اصلاح خودکار فعال نیست. "
            "مراحل زیر را خودتان در پنل مدیریت / کد منبع / هاست انجام دهید. "
            "پس از فعال‌سازی دسترسی، می‌توانید دوباره به Manager بگویید اصلاح‌ها را خودش اعمال کند."
        )
    lines.extend(["", "## اقدامات پیشنهادی", ""])

    if not report.findings:
        lines.append("اقدام اصلاحی خاصی ثبت نشد.")
    else:
        for index, finding in enumerate(report.findings, start=1):
            manual = _manual_steps(finding)
            auto_note = (
                "قابل بررسی برای اصلاح خودکار پس از دسترسی معتبر."
                if finding.requires_access or mode == "post_contract"
                else "اغلب از طریق تنظیمات عمومی یا SEO قابل اصلاح است."
            )
            lines.extend(
                [
                    f"### {index}. {finding.title}",
                    f"- **دسته:** {finding.category}",
                    f"- **پیشنهاد اصلی:** {finding.recommendation}",
                    f"- **سختی تخمینی:** {finding.effort}",
                    f"- **وضعیت اصلاح خودکار:** {auto_note}",
                    f"- **مراحل دستی:**",
                    *[f"  {step}" for step in manual],
                    "",
                ]
            )

    lines.extend(
        [
            "## اگر خودتان اصلاح می‌کنید",
            "",
            "1. از فایل مشکلات، موارد با شدت «زیاد» را اول انجام دهید.",
            "2. پس از هر تغییر مهم، صفحه را در موبایل و دسکتاپ بازبینی کنید.",
            "3. دوباره از Manager بخواهید سایت را اسکن کند تا وضعیت جدید ثبت شود.",
            "",
            "## اگر می‌خواهید Manager خودش اصلاح کند",
            "",
            "دسترسی معتبر (مثلاً برای WordPress: Application Password با نقش مناسب) را فعال کنید و بگویید:",
            "«دسترسی دادم؛ مشکلات سایت را اصلاح کن.»",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _manual_steps(finding: AuditFinding) -> list[str]:
    category = finding.category
    title = finding.title
    if category == "SEO" and "عنوان" in title:
        return [
            "1. در قالب یا افزونه SEO، فیلد Title صفحه را پر کنید.",
            "2. عنوان یکتا و توصیفی (حدود ۵۰–۶۰ کاراکتر) بنویسید.",
            "3. صفحه را ذخیره و کش را پاک کنید.",
        ]
    if category == "SEO" and "Meta" in title:
        return [
            "1. Meta Description را در تنظیمات SEO صفحه اضافه کنید.",
            "2. توضیح حدود ۱۲۰–۱۶۰ کاراکتر و مرتبط با محتوا بنویسید.",
            "3. ذخیره و انتشار مجدد.",
        ]
    if category == "SEO" and "H1" in title:
        return [
            "1. در محتوای اصلی صفحه یک تگ H1 یکتا قرار دهید.",
            "2. از چند H1 تکراری در یک صفحه پرهیز کنید.",
            "3. قالب را بررسی کنید که H1 را مخفی یا حذف نکند.",
        ]
    if category == "Accessibility":
        return [
            "1. برای هر تصویر معنادار، متن جایگزین (alt) توصیفی بگذارید.",
            "2. تصاویر تزئینی را با alt خالی علامت‌گذاری کنید.",
            "3. ذخیره و بررسی با ابزار صفحه‌خوان در صورت امکان.",
        ]
    if category == "Performance":
        return [
            "1. تصاویر سنگین را فشرده و به فرمت مدرن تبدیل کنید.",
            "2. کش و CDN را فعال کنید.",
            "3. اسکریپت‌های غیرضروری را به تعویق بیندازید یا حذف کنید.",
        ]
    if category == "Links":
        return [
            "1. وضعیت HTTP صفحه را در سرور/هاست بررسی کنید.",
            "2. مسیر اشتباه، مجوز فایل یا خطای برنامه را برطرف کنید.",
            "3. لینک‌های داخلی شکسته را اصلاح کنید.",
        ]
    return [
        f"1. پیشنهاد: {finding.recommendation}",
        "2. تغییر را در محیط تست اعمال کنید.",
        "3. پس از تأیید، روی محیط اصلی منتشر کنید.",
    ]
