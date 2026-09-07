# -*- coding: utf-8 -*-
"""
knowledge_base.py
مسؤول عن حفظ ملخص كل محاضرة على حدة، وتحديث "المرجع الشامل" اللي بيجمع كل المحاضرات
اللي اتبعتت لحد دلوقتي في مكان واحد عشان يتخصص بيه الطلاب.

كل محاضرة بتتحفظ بصيغتين:
  - .md   → النسخة الخام (للتعديل/النسخ السريع).
  - .html → نسخة منسقة بتصميم جاهز للنشر أو الطباعة (تفتح مباشرة في أي متصفح).
نفس الكلام بينطبق على "المرجع الشامل".
"""

import json
import os
from datetime import datetime

import html_design

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")
MASTER_REFERENCE_PATH = os.path.join(BASE_DIR, "المرجع_الشامل.md")
MASTER_REFERENCE_HTML_PATH = os.path.join(BASE_DIR, "المرجع_الشامل.html")
INDEX_PATH = os.path.join(BASE_DIR, "lectures_index.json")

os.makedirs(SUMMARIES_DIR, exist_ok=True)


def _load_index():
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_index(index):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _safe_filename(name: str) -> str:
    keep = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    return keep.strip() or "محاضرة"


def save_lecture_summary(lecture_name: str, source_path: str, summary_text: str) -> str:
    """
    يحفظ ملخص المحاضرة (Markdown + HTML منسق)، ويضيفها لفهرس المحاضرات،
    ويحدّث المرجع الشامل بنسختيه.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    source_file = os.path.basename(source_path)

    filename = f"{_safe_filename(lecture_name)}.md"
    html_filename = f"{_safe_filename(lecture_name)}.html"
    file_path = os.path.join(SUMMARIES_DIR, filename)
    html_path = os.path.join(SUMMARIES_DIR, html_filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {lecture_name}\n\n")
        f.write(f"*المصدر: {source_file} — تمت المعالجة في {timestamp}*\n\n")
        f.write(summary_text)

    lecture_html = html_design.render_lecture_page(
        lecture_name=lecture_name,
        source_file=source_file,
        processed_at=timestamp,
        summary_markdown=summary_text,
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(lecture_html)

    index = _load_index()
    index = [item for item in index if item["lecture_name"] != lecture_name]  # امنع التكرار
    index.append(
        {
            "lecture_name": lecture_name,
            "source_file": source_file,
            "summary_file": filename,
            "summary_html_file": html_filename,
            "processed_at": timestamp,
        }
    )
    _save_index(index)

    _rebuild_master_reference(index)
    return file_path


def _rebuild_master_reference(index):
    """يعيد بناء ملف المرجع الشامل (Markdown + HTML) من كل الملخصات المحفوظة."""
    lines = ["# 📚 المرجع الشامل لكل المحاضرات\n"]
    lines.append(f"*آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    lines.append(f"*عدد المحاضرات المُلخّصة حتى الآن: {len(index)}*\n")

    lines.append("\n## 🗂️ فهرس المحاضرات\n")
    for i, item in enumerate(index, start=1):
        lines.append(f"{i}. [{item['lecture_name']}](#{_anchor(item['lecture_name'])})")

    lines.append("\n---\n")

    for item in index:
        summary_path = os.path.join(SUMMARIES_DIR, item["summary_file"])
        if not os.path.exists(summary_path):
            continue
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines.append(f"\n<a name=\"{_anchor(item['lecture_name'])}\"></a>\n")
        lines.append(content)
        lines.append("\n---\n")

    with open(MASTER_REFERENCE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    def _summary_lookup(lecture_name):
        path = get_lecture_summary_path(lecture_name)
        if not path or not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        # نشيل العنوان وسطر المصدر بتوع بداية الملف عشان ميتكررش في المرجع الشامل
        parts = raw.split("\n\n", 2)
        return parts[2] if len(parts) == 3 else raw

    master_html = html_design.render_master_reference_page(index, _summary_lookup)
    with open(MASTER_REFERENCE_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(master_html)


def _anchor(text: str) -> str:
    return "".join(c for c in text if c.isalnum())


def get_all_lectures():
    return _load_index()


def get_master_reference_path() -> str:
    if not os.path.exists(MASTER_REFERENCE_PATH):
        _rebuild_master_reference(_load_index())
    return MASTER_REFERENCE_PATH


def get_master_reference_html_path() -> str:
    if not os.path.exists(MASTER_REFERENCE_HTML_PATH):
        _rebuild_master_reference(_load_index())
    return MASTER_REFERENCE_HTML_PATH


def get_lecture_summary_path(lecture_name: str) -> str:
    for item in _load_index():
        if item["lecture_name"] == lecture_name:
            return os.path.join(SUMMARIES_DIR, item["summary_file"])
    return ""


def get_lecture_summary_html_path(lecture_name: str) -> str:
    for item in _load_index():
        if item["lecture_name"] == lecture_name:
            html_file = item.get("summary_html_file")
            if html_file:
                return os.path.join(SUMMARIES_DIR, html_file)
    return ""
