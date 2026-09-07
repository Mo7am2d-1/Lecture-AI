# -*- coding: utf-8 -*-
"""
transcriber.py
تفريغ صوتي محلي بالكامل (بدون أي API مدفوع) باستخدام مكتبة faster-whisper.
أول مرة هتشغل تفريغ، المكتبة هتنزل وزن الموديل مرة واحدة وتخزنه محلياً.
"""

_model_cache = {}


def _get_model(model_size: str = "small"):
    """يحمّل موديل Whisper المحلي مرة واحدة ويحتفظ بيه في الذاكرة."""
    if model_size not in _model_cache:
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            raise RuntimeError(
                "مكتبة faster-whisper مش متثبتة. ثبتها بالأمر:\n"
                "pip install faster-whisper\n"
                "ولازم يكون عندك ffmpeg متثبت على الجهاز كمان."
            ) from e

        # compute_type="int8" أخف وأسرع على المعالج العادي (بدون كارت شاشة)
        _model_cache[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
    return _model_cache[model_size]


def transcribe_media(path: str, model_size: str = "small", progress_callback=None) -> str:
    """
    يفرّغ ملف صوت أو فيديو إلى نص مكتوب.
    model_size: tiny / base / small / medium / large-v3 (الأكبر أدق بس أبطأ).
    """
    model = _get_model(model_size)

    if progress_callback:
        progress_callback("جاري تحليل الصوت وتحويله لنص (Whisper)...")

    segments, info = model.transcribe(path, language=None, vad_filter=True)

    text_parts = []
    for segment in segments:
        text_parts.append(segment.text.strip())
        if progress_callback and len(text_parts) % 20 == 0:
            progress_callback(f"تم تفريغ {len(text_parts)} جملة لحد دلوقتي...")

    full_text = " ".join(text_parts).strip()

    if progress_callback:
        detected_lang = getattr(info, "language", "unknown")
        progress_callback(f"اكتمل التفريغ الصوتي (اللغة المكتشفة: {detected_lang}).")

    return full_text
