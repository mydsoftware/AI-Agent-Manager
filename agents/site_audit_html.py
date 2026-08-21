from __future__ import annotations

from html import escape

from agents.site_audit_report import SiteAuditReport


class SiteAuditHtmlRenderer:
    """تبدیل گزارش ممیزی به HTML مستقل و راست‌به‌چپ."""

    def render(self, report: SiteAuditReport, title: str = "گزارش ممیزی سایت") -> str:
        def esc(value: object) -> str:
            return escape(str(value), quote=True)

        page_rows = "".join(
            f"<tr><td>{esc(item['url'])}</td><td>{esc(item['status'])}</td><td>{esc(item['title'])}</td>"
            f"<td>{esc(item.get('canonical_url') or '—')}</td><td>{esc(item.get('seo_score', '—'))}</td>"
            f"<td>{esc(item.get('seo_status', '—'))}</td></tr>"
            for item in report.seo_items
        ) or '<tr><td colspan="6">صفحه‌ای ثبت نشده است.</td></tr>'

        redirect_rows = "".join(
            f"<tr><td>{esc(item['source_url'])}</td><td>{esc(item['status'])}</td>"
            f"<td>{esc(item['destination_url'])}</td></tr>"
            for item in report.redirect_items
        ) or '<tr><td colspan="3">Redirectی ثبت نشده است.</td></tr>'

        duplicate_rows = "".join(
            f"<tr><td>{esc(item['canonical_url'] or item['key'])}</td>"
            f"<td>{esc('، '.join(item['urls']))}</td></tr>"
            for item in report.duplicate_items
        ) or '<tr><td colspan="2">Duplicateای ثبت نشده است.</td></tr>'

        error_rows = "".join(
            f"<tr><td>{esc(url)}</td><td>{esc(error)}</td></tr>"
            for url, error in report.errors.items()
        ) or '<tr><td colspan="2">خطایی ثبت نشده است.</td></tr>'

        return f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>
body{{font-family:Tahoma,Arial,sans-serif;background:#f5f7fb;color:#172033;margin:0;padding:24px}}
main{{max-width:1200px;margin:auto}}
h1{{margin-bottom:24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:28px}}
.card{{background:#fff;border:1px solid #e5e9f2;border-radius:12px;padding:18px}}
.card b{{display:block;font-size:28px;margin-top:8px}}
.score{{font-size:36px!important}}
section{{background:#fff;border:1px solid #e5e9f2;border-radius:12px;padding:18px;margin-bottom:20px;overflow:auto}}
table{{width:100%;border-collapse:collapse;min-width:850px}}
th,td{{padding:10px;border-bottom:1px solid #edf0f5;text-align:right;vertical-align:top}}
th{{background:#f8f9fc}}
</style>
</head>
<body><main>
<h1>{esc(title)}</h1>
<div class="grid">
<div class="card">امتیاز کلی SEO<b class="score">{report.seo_score}/100</b></div>
<div class="card">وضعیت SEO<b>{esc(report.seo_status)}</b></div>
<div class="card">مشکلات SEO<b>{report.seo_issues}</b></div>
<div class="card">صفحات اسکن‌شده<b>{report.pages_scanned}</b></div>
<div class="card">خطاها<b>{report.pages_failed}</b></div>
<div class="card">Redirect<b>{report.redirects}</b></div>
<div class="card">Canonical مفقود<b>{report.missing_canonical}</b></div>
<div class="card">Canonical خارجی<b>{report.external_canonical}</b></div>
<div class="card">گروه Duplicate<b>{report.duplicate_groups}</b></div>
</div>
<section><h2>SEO صفحات</h2><table><thead><tr><th>URL</th><th>وضعیت HTTP</th><th>عنوان</th><th>Canonical</th><th>امتیاز SEO</th><th>وضعیت SEO</th></tr></thead><tbody>{page_rows}</tbody></table></section>
<section><h2>Redirectها</h2><table><thead><tr><th>مبدأ</th><th>وضعیت</th><th>مقصد</th></tr></thead><tbody>{redirect_rows}</tbody></table></section>
<section><h2>Duplicateها</h2><table><thead><tr><th>Canonical</th><th>URLها</th></tr></thead><tbody>{duplicate_rows}</tbody></table></section>
<section><h2>خطاها</h2><table><thead><tr><th>URL</th><th>خطا</th></tr></thead><tbody>{error_rows}</tbody></table></section>
</main></body></html>"""
