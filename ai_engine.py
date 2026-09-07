# -*- coding: utf-8 -*-
"""
ai_engine.py
مسؤول عن التلخيص والتحليل باستخدام موديل مجاني شغال محلياً على جهازك عن طريق Ollama.
لازم يكون عندك Ollama متثبت وشغال (راجع README.md لطريقة التثبيت).
"""

import requests

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"   # موديل مجاني كويس مع العربي. لو جهازك ضعيف استخدم "llama3.2:3b"

# طول أقصى تقريبي (بالحروف) للقطعة الواحدة قبل ما نبعتها للموديل
CHUNK_SIZE = 6000


def call_ollama(prompt: str, model: str = DEFAULT_MODEL, host: str = DEFAULT_OLLAMA_HOST) -> str:
    """يبعت الطلب لموديل Ollama المحلي ويرجع الرد كنص."""
    url = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    try:
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            "مش قادر أوصل لـ Ollama. تأكد إن البرنامج شغال بالأمر:\n"
            "ollama serve\n"
            f"وإن الموديل '{model}' متحمّل (ollama pull {model})."
        ) from e
    return response.json().get("response", "").strip()


def _split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE):
    """يقسم النص الطويل لقطع أصغر عشان تدخل في حدود الموديل."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks if chunks else [text]


def _map_prompt(chunk: str, lecture_name: str, part_num: int, total_parts: int) -> str:
    return f"""أنت مساعد تعليمي بيحلل محاضرات جامعية باللغة العربية.
دي جزء رقم {part_num} من {total_parts} من محاضرة اسمها "{lecture_name}".
اقرأ المحتوى ده كويس ولخصه بدقة، مع الحفاظ على أي معادلات أو تعريفات أو مصطلحات تقنية مهمة زي ما هي:

النص:
\"\"\"
{chunk}
\"\"\"

اكتب ملخص منظم للجزء ده فقط (من غير مقدمات زيادة)."""


def _reduce_prompt(lecture_name: str, partial_summaries: str) -> str:
    return f"""أنت مساعد تعليمي متخصص في مساعدة الطلاب على المذاكرة.
تحت مجموعة ملخصات جزئية لمحاضرة كاملة اسمها "{lecture_name}". اعمل منها تحليل نهائي متكامل بالشكل ده بالظبط (استخدم نفس العناوين، ونفس مستوى العناوين ##، من غير ما تضيف أي عناوين فرعية زي ### أو #):

## 📌 ملخص شامل
فقرة أو فقرتين نثر متصل (من غير عناوين فرعية) تلخص محتوى المحاضرة كله بشكل مترابط.

## 🧠 المفاهيم الأساسية
قائمة نقطية (- ) فقط، كل نقطة بالشكل: **اسم المفهوم**: شرح مبسط في سطر أو سطرين.

## ✅ نقاط لازم تذاكرها كويس
قائمة نقطية (- ) فقط، كل نقطة جملة واحدة واضحة ومباشرة.

## ❓ أسئلة متوقعة للمراجعة الذاتية
قائمة مرقّمة (1. 2. 3. ...) من 5 إلى 8 أسئلة الطالب يقدر يمتحن نفسه بيها على المحاضرة دي.

قواعد تنسيق مهمة يجب الالتزام بها:
- استخدم فقط ## للعناوين الأربعة دي بالظبط، وممنوع أي عنوان تاني (لا ### ولا ####).
- استخدم **نص عريض** فقط للمصطلحات والمفاهيم المهمة، مش لجمل كاملة.
- لو فيه أوامر برمجية أو أكواد (زي دوال بايثون)، ضعها بين backticks مفردة `code` عشان تتنسق صح.
- ممنوع تكرار نفس المفهوم بنفس الصياغة في أكتر من قسم.
- ابدأ مباشرة بالعنوان الأول من غير أي مقدمة قبله.

الملخصات الجزئية:
\"\"\"
{partial_summaries}
\"\"\"
"""


def summarize_lecture(
    text: str,
    lecture_name: str,
    model: str = DEFAULT_MODEL,
    host: str = DEFAULT_OLLAMA_HOST,
    progress_callback=None,
) -> str:
    """
    يلخص ويحلل محتوى محاضرة واحدة بالكامل (المرجع بتاعه هو نص المحاضرة دي بس).
    بيستخدم أسلوب map-reduce: يلخص كل جزء لوحده، وبعدين يدمجهم في تحليل نهائي واحد.
    """
    if not text or not text.strip():
        return "⚠️ لم يتم العثور على نص قابل للتلخيص في هذه المحاضرة."

    chunks = _split_into_chunks(text)
    partial_summaries = []

    for idx, chunk in enumerate(chunks, start=1):
        if progress_callback:
            progress_callback(f"جاري تلخيص الجزء {idx} من {len(chunks)} من '{lecture_name}'...")
        prompt = _map_prompt(chunk, lecture_name, idx, len(chunks))
        partial = call_ollama(prompt, model=model, host=host)
        partial_summaries.append(f"[جزء {idx}]\n{partial}")

    if progress_callback:
        progress_callback("جاري دمج الملخصات الجزئية في تحليل نهائي...")

    combined = "\n\n".join(partial_summaries)
    final_summary = call_ollama(_reduce_prompt(lecture_name, combined), model=model, host=host)

    return final_summary
