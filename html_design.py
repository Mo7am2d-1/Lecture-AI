# -*- coding: utf-8 -*-
"""
html_design.py
مسؤول عن تحويل ملخصات الماركداون إلى صفحات HTML جاهزة للنشر للطلاب،
بتصميم عربي (RTL) احترافي وهادئ، مناسب للمشاركة أو الطباعة.

الفكرة: الكود بيولد نص Markdown زي ما هو (عشان يفضل خفيف ومتوافق مع
knowledge_base.py الحالي)، وده الملف اللي بيحوّله لصفحة HTML منسقة.
"""

import html as _html
import re
from datetime import datetime

try:
    import markdown as _markdown_lib

    _HAS_MARKDOWN = True
except ImportError:
    _HAS_MARKDOWN = False


APP_TITLE = "مساعد تلخيص وتحليل المحاضرات"

# أيقونة بسيطة (SVG) تُستخدم كفافيكون في تبويب المتصفح
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E"
    "%3Crect width='24' height='24' rx='5' fill='%231e293b'/%3E"
    "%3Cpath d='M12 6l8 3.5-8 3.5-8-3.5L12 6z' fill='%2360a5fa'/%3E"
    "%3Cpath d='M6 12.2v3.3c0 1 2.7 2.5 6 2.5s6-1.5 6-2.5v-3.3l-6 2.6-6-2.6z' fill='%2360a5fa'/%3E"
    "%3C/svg%3E"
)

# لون هادئ مختلف لكل قسم من أقسام الملخص (بترتيب ظهورها) — درجات مطفأة
# احترافية بدل الألوان الصريحة، تُستخدم فقط كخط جانبي رفيع + لون نص العنوان.
SECTION_ACCENTS = ["#2563eb", "#0f766e", "#b45309", "#6d28d9"]

BASE_CSS = """
:root {
    --page-bg: #f3f4f6;
    --card-bg: #ffffff;
    --border: #e5e7eb;
    --text-main: #1f2937;
    --text-muted: #6b7280;
    --primary: #1e3a8a;
    --primary-soft: #eff6ff;
    --radius: 12px;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    margin: 0;
    background: var(--page-bg);
    color: var(--text-main);
    font-family: "Tajawal", "Segoe UI", Tahoma, Arial, sans-serif;
    line-height: 1.85;
    direction: rtl;
    font-size: 16px;
}

.page-wrap {
    max-width: 880px;
    margin: 0 auto;
    padding: 32px 20px 60px;
}

/* ---------- Hero header ---------- */
.hero {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    border-radius: var(--radius);
    padding: 28px 30px;
    margin-bottom: 24px;
    border: 1px solid #0f172a;
}
.hero .eyebrow {
    font-size: 12.5px;
    color: #93c5fd;
    margin: 0 0 8px;
    letter-spacing: 0.3px;
    font-weight: 600;
}
.hero h1 {
    margin: 0 0 14px;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 0.2px;
}
.hero .meta {
    font-size: 13px;
    color: #cbd5e1;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.hero .meta span {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 4px 12px;
    border-radius: 8px;
}

/* ---------- Table of contents (mobile pills, hidden on desktop) ---------- */
.toc-pills {
    display: none;
    flex-wrap: wrap;
    gap: 8px;
    position: sticky;
    top: 0;
    background: var(--page-bg);
    padding: 10px 0 14px;
    z-index: 5;
}
.toc-pills a {
    background: var(--card-bg);
    border: 1px solid var(--border);
    color: var(--text-main);
    text-decoration: none;
    font-size: 12.5px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 8px;
}
.toc-pills a:hover { border-color: var(--primary); color: var(--primary); }

/* ---------- Master layout: sidebar + content (docs-style) ---------- */
.master-layout {
    display: flex;
    align-items: flex-start;
    gap: 22px;
}
.master-sidebar {
    width: 230px;
    flex-shrink: 0;
    position: sticky;
    top: 20px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
}
.master-sidebar h2 {
    margin: 0 0 4px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-muted);
    font-weight: 700;
}
.master-sidebar .count {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0 0 12px;
}
.master-sidebar ol {
    list-style: none;
    margin: 0;
    padding: 0;
    counter-reset: nav;
}
.master-sidebar li {
    counter-increment: nav;
    margin-bottom: 2px;
}
.master-sidebar a {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-main);
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 600;
    padding: 7px 8px;
    border-radius: 8px;
}
.master-sidebar a::before {
    content: counter(nav);
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 5px;
    background: var(--primary-soft);
    color: var(--primary);
    font-size: 11px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}
.master-sidebar a:hover { background: #f8fafc; color: var(--primary); }
.master-content { flex: 1; min-width: 0; }

@media (max-width: 820px) {
    .master-sidebar { display: none; }
    .toc-pills { display: flex; }
}

/* ---------- Lecture card ---------- */
.lecture-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 28px 14px;
    margin-bottom: 24px;
}
.lecture-card .lecture-title {
    font-size: 19px;
    font-weight: 800;
    margin: 0 0 4px;
    color: var(--text-main);
}
.lecture-card .lecture-source {
    font-size: 12.5px;
    color: var(--text-muted);
    margin: 0 0 18px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}

/* ---------- Content typography (converted from Markdown) ---------- */
.content h2 {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 15.5px;
    font-weight: 800;
    margin: 28px 0 14px;
    padding-bottom: 9px;
    border-bottom: 2px solid var(--border);
    color: var(--text-main);
}
.content h2 .icon-dot {
    width: 8px;
    height: 8px;
    border-radius: 2px;
    flex-shrink: 0;
    display: inline-block;
}
.content h2:nth-of-type(4n+1) { border-bottom-color: #2563eb; }
.content h2:nth-of-type(4n+1) .icon-dot { background: #2563eb; }
.content h2:nth-of-type(4n+2) { border-bottom-color: #0f766e; }
.content h2:nth-of-type(4n+2) .icon-dot { background: #0f766e; }
.content h2:nth-of-type(4n+3) { border-bottom-color: #b45309; }
.content h2:nth-of-type(4n+3) .icon-dot { background: #b45309; }
.content h2:nth-of-type(4n+4) { border-bottom-color: #6d28d9; }
.content h2:nth-of-type(4n+4) .icon-dot { background: #6d28d9; }

.content h3 {
    font-size: 14.5px;
    font-weight: 700;
    margin: 16px 0 8px;
    color: var(--text-main);
}

.content p { margin: 0 0 14px; color: #374151; }

.content ul, .content ol {
    margin: 0 0 18px;
    padding: 0;
}
.content ul { list-style: none; }
.content ul li {
    position: relative;
    padding-inline-start: 22px;
    padding-inline-end: 2px;
    margin-bottom: 9px;
    color: #374151;
}
.content ul li::before {
    content: "";
    position: absolute;
    right: 4px;
    top: 9px;
    width: 6px;
    height: 6px;
    border-radius: 1px;
    background: #94a3b8;
}

/* أسئلة المراجعة الذاتية كبطاقات مرقّمة */
.content ol {
    counter-reset: q;
}
.content ol li {
    list-style: none;
    counter-increment: q;
    background: #f9fafb;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 42px 10px 14px;
    position: relative;
    margin-bottom: 8px;
    color: #374151;
}
.content ol li::before {
    content: counter(q);
    position: absolute;
    right: 10px;
    top: 9px;
    background: var(--primary);
    color: #fff;
    width: 20px;
    height: 20px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

.content strong {
    color: var(--primary);
    font-weight: 800;
}

.content code {
    direction: ltr;
    unicode-bidi: embed;
    display: inline-block;
    background: #f1f5f9;
    color: #0f172a;
    padding: 1px 6px;
    border-radius: 5px;
    font-family: "Consolas", "SFMono-Regular", Menlo, monospace;
    font-size: 12.5px;
    border: 1px solid #e2e8f0;
}
.content pre {
    direction: ltr;
    text-align: left;
    background: #0f172a;
    color: #e2e8f0;
    padding: 14px 16px;
    border-radius: 10px;
    overflow-x: auto;
    font-size: 13px;
}
.content pre code { background: none; color: inherit; padding: 0; border: none; }

.content hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 26px 0;
}

.content table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 0 16px;
    font-size: 13.5px;
}
.content table th, .content table td {
    border: 1px solid var(--border);
    padding: 8px 10px;
    text-align: right;
}
.content table th { background: #f9fafb; font-weight: 700; }

/* ---------- Footer ---------- */
.page-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 11.5px;
    margin-top: 26px;
}

/* ---------- Print ---------- */
@media print {
    body { background: #fff; }
    .toc-pills, .master-sidebar { display: none; }
    .master-layout { display: block; }
    .lecture-card {
        border: none;
        box-shadow: none;
        page-break-inside: avoid;
        page-break-after: always;
        padding: 0;
    }
    .hero { border: none; }
}

@media (max-width: 480px) {
    .hero h1 { font-size: 20px; }
    .lecture-card { padding: 18px 16px 8px; }
}
"""

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" '
    'rel="stylesheet">'
)


def _markdown_to_html(md_text: str) -> str:
    """يحوّل نص Markdown لـ HTML. لو مكتبة markdown غير متاحة، بيعمل تحويل بسيط احتياطي."""
    if _HAS_MARKDOWN:
        html_out = _markdown_lib.markdown(
            md_text, extensions=["tables", "fenced_code", "sane_lists"]
        )
    else:
        html_out = _fallback_markdown_to_html(md_text)
    # نضيف نقطة لونية صغيرة (icon-dot) جوه كل h2 عشان تتلوّن حسب ترتيب القسم
    return re.sub(r"<h2>(.*?)</h2>", r'<h2><span class="icon-dot"></span>\1</h2>', html_out)


def _fallback_markdown_to_html(md_text: str) -> str:
    """تحويل احتياطي بسيط جداً لو مكتبة markdown مش متثبتة (pip install markdown)."""
    lines = md_text.splitlines()
    out = []
    in_list = False
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if line.startswith("### "):
            out.append(f"<h3>{_html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{_html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{_html.escape(line[2:])}</h1>")
        elif line.strip() in ("---", "***"):
            out.append("<hr>")
        elif re.match(r"^[-*]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_html.escape(line.split(' ', 1)[1])}</li>")
        else:
            out.append(f"<p>{_html.escape(line)}</p>")
    if in_list:
        out.append("</ul>")
    text = "\n".join(out)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def _head(title: str) -> str:
    return f"""<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html.escape(title)}</title>
<link rel="icon" href="{FAVICON}">
{FONT_LINK}
<style>{BASE_CSS}</style>"""


def render_lecture_page(lecture_name: str, source_file: str, processed_at: str, summary_markdown: str) -> str:
    """يبني صفحة HTML مستقلة لمحاضرة واحدة، جاهزة للنشر/الطباعة."""
    body_html = _markdown_to_html(summary_markdown)
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
{_head(lecture_name)}
</head>
<body>
<div class="page-wrap">
  <div class="hero">
    <p class="eyebrow">{_html.escape(APP_TITLE)}</p>
    <h1>{_html.escape(lecture_name)}</h1>
    <div class="meta">
      <span>المصدر: {_html.escape(source_file)}</span>
      <span>{_html.escape(processed_at)}</span>
    </div>
  </div>
  <div class="lecture-card">
    <div class="content">
      {body_html}
    </div>
  </div>
  <p class="page-footer">تم إنشاء هذا الملخص تلقائياً بواسطة {_html.escape(APP_TITLE)}</p>
</div>
</body>
</html>"""


def render_master_reference_page(index, summaries_lookup) -> str:
    """
    يبني صفحة HTML واحدة تجمع كل المحاضرات، بتصميم يشبه مواقع التوثيق:
    قايمة جانبية ثابتة للتنقل + محتوى المحاضرات، مع نسخة موبايل (pills أفقية).
    index: قايمة عناصر الفهرس [{lecture_name, source_file, processed_at, ...}]
    summaries_lookup: دالة بتاخد lecture_name وترجع نص الملخص Markdown بتاعه
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    pills = "\n".join(
        f'<a href="#{_anchor(item["lecture_name"])}">{_html.escape(item["lecture_name"])}</a>'
        for item in index
    )

    sidebar_items = "\n".join(
        f'<li><a href="#{_anchor(item["lecture_name"])}">{_html.escape(item["lecture_name"])}</a></li>'
        for item in index
    )

    cards = []
    for item in index:
        md_text = summaries_lookup(item["lecture_name"])
        if md_text is None:
            continue
        body_html = _markdown_to_html(md_text)
        cards.append(
            f"""
  <div class="lecture-card" id="{_anchor(item['lecture_name'])}">
    <p class="lecture-title">{_html.escape(item['lecture_name'])}</p>
    <p class="lecture-source">{_html.escape(item.get('source_file', ''))} — {_html.escape(item.get('processed_at', ''))}</p>
    <div class="content">
      {body_html}
    </div>
  </div>"""
        )
    cards_html = "\n".join(cards)

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
{_head("المرجع الشامل لكل المحاضرات")}
</head>
<body>
<div class="page-wrap" style="max-width: 1100px;">
  <div class="hero">
    <p class="eyebrow">{_html.escape(APP_TITLE)}</p>
    <h1>المرجع الشامل لكل المحاضرات</h1>
    <div class="meta">
      <span>عدد المحاضرات: {len(index)}</span>
      <span>آخر تحديث: {now}</span>
    </div>
  </div>

  <div class="toc-pills">
    {pills}
  </div>

  <div class="master-layout">
    <aside class="master-sidebar">
      <h2>المحاضرات</h2>
      <p class="count">{len(index)} محاضرة</p>
      <ol>
        {sidebar_items}
      </ol>
    </aside>
    <div class="master-content">
      {cards_html}
      <p class="page-footer">تم إنشاء هذا المرجع تلقائياً بواسطة {_html.escape(APP_TITLE)}</p>
    </div>
  </div>
</div>
</body>
</html>"""


def _anchor(text: str) -> str:
    return "".join(c for c in text if c.isalnum()) or "s"
