# -*- coding: utf-8 -*-
"""
extractors.py
مسؤول عن استخراج النص الخام من ملفات المحاضرات المختلفة (PDF / Word / نصوص).
استخراج الصوت والفيديو موجود في transcriber.py لأنه محتاج مكتبات تانية.
"""

import os


def extract_text_from_pdf(path: str) -> str:
    """يستخرج النص من ملف PDF صفحة بصفحة."""
    import pdfplumber

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(f"\n--- صفحة {i} ---\n{page_text}")
    return "\n".join(text_parts).strip()


def extract_text_from_docx(path: str) -> str:
    """يستخرج النص من ملف Word (.docx)."""
    import docx

    document = docx.Document(path)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

    # استخراج أي جداول موجودة في الملف كمان
    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            if row_text.strip(" |"):
                paragraphs.append(row_text)

    return "\n".join(paragraphs).strip()


def extract_text_from_txt(path: str) -> str:
    """يقرأ ملف نصي عادي."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


# الصيغ اللي بنقدر نتعامل معاها مباشرة (بدون تفريغ صوتي)
DIRECT_TEXT_EXTENSIONS = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_docx,
    ".txt": extract_text_from_txt,
    ".md": extract_text_from_txt,
}

# الصيغ اللي محتاجة تفريغ صوتي (فيديو / صوت)
MEDIA_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".mp3", ".wav", ".m4a", ".aac"}


def get_file_kind(path: str) -> str:
    """يرجع نوع الملف: 'text' أو 'media' أو 'unknown'."""
    ext = os.path.splitext(path)[1].lower()
    if ext in DIRECT_TEXT_EXTENSIONS:
        return "text"
    if ext in MEDIA_EXTENSIONS:
        return "media"
    return "unknown"


def extract_text(path: str, progress_callback=None) -> str:
    """
    نقطة الدخول الموحدة: بتاخد مسار أي ملف محاضرة وترجع النص المستخرج منه.
    لو الملف صوت/فيديو، بتستخدم transcriber.py لتفريغه أولاً.
    """
    kind = get_file_kind(path)
    ext = os.path.splitext(path)[1].lower()

    if kind == "text":
        if progress_callback:
            progress_callback(f"جاري استخراج النص من الملف ({ext}) ...")
        return DIRECT_TEXT_EXTENSIONS[ext](path)

    if kind == "media":
        if progress_callback:
            progress_callback("الملف صوت/فيديو — جاري التفريغ الصوتي (ممكن ياخد وقت)...")
        from transcriber import transcribe_media

        return transcribe_media(path, progress_callback=progress_callback)

    raise ValueError(f"صيغة الملف غير مدعومة: {ext}")
