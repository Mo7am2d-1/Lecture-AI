# -*- coding: utf-8 -*-
"""
app.py
الواجهة الرسومية الرئيسية للبرنامج.
شغّله بالأمر: python app.py
"""

import os
import queue
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk

import ai_engine
import extractors
import knowledge_base

FILE_TYPES = [
    ("كل الملفات المدعومة", "*.pdf *.docx *.txt *.md *.mp4 *.mov *.mkv *.avi *.mp3 *.wav *.m4a *.aac"),
    ("PDF", "*.pdf"),
    ("Word", "*.docx"),
    ("نصوص", "*.txt *.md"),
    ("فيديو / صوت", "*.mp4 *.mov *.mkv *.avi *.mp3 *.wav *.m4a *.aac"),
]


class LectureAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مساعد تلخيص وتحليل المحاضرات")
        self.root.geometry("1000x650")

        self.model_name = tk.StringVar(value=ai_engine.DEFAULT_MODEL)
        self.ollama_host = tk.StringVar(value=ai_engine.DEFAULT_OLLAMA_HOST)

        self.log_queue = queue.Queue()
        self.pending_files = []  # [(display_name, path)]

        self._build_ui()
        self._refresh_lectures_list()
        self.root.after(200, self._poll_log_queue)

    # ---------------------------------------------------------------- UI ---
    def _build_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="اسم الموديل المحلي (Ollama):").pack(side="right", padx=4)
        ttk.Entry(top_frame, textvariable=self.model_name, width=20, justify="right").pack(
            side="right", padx=4
        )
        ttk.Label(top_frame, text="عنوان Ollama:").pack(side="right", padx=4)
        ttk.Entry(top_frame, textvariable=self.ollama_host, width=22, justify="right").pack(
            side="right", padx=4
        )

        main_pane = ttk.Panedwindow(self.root, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=10, pady=10)

        # --- اللوحة اليمين: قائمة المحاضرات ---
        left_frame = ttk.Frame(main_pane, width=320)
        main_pane.add(left_frame, weight=1)

        ttk.Label(left_frame, text="📄 الملفات المضافة للمعالجة", font=("Arial", 11, "bold")).pack(
            anchor="e", pady=(0, 4)
        )
        self.pending_listbox = tk.Listbox(left_frame, height=8, justify="right")
        self.pending_listbox.pack(fill="x", pady=4)

        btns_frame = ttk.Frame(left_frame)
        btns_frame.pack(fill="x", pady=4)
        ttk.Button(btns_frame, text="➕ إضافة محاضرة", command=self.add_files).pack(
            side="right", padx=2
        )
        ttk.Button(btns_frame, text="🚀 معالجة الكل", command=self.process_all).pack(
            side="right", padx=2
        )

        ttk.Separator(left_frame).pack(fill="x", pady=8)

        ttk.Label(left_frame, text="✅ المحاضرات المُلخّصة", font=("Arial", 11, "bold")).pack(
            anchor="e", pady=(0, 4)
        )
        self.done_listbox = tk.Listbox(left_frame, height=12, justify="right")
        self.done_listbox.pack(fill="both", expand=True, pady=4)
        self.done_listbox.bind("<<ListboxSelect>>", self._on_select_done_lecture)
        self.done_listbox.bind("<Double-Button-1>", self._on_open_done_lecture_html)

        ttk.Button(
            left_frame, text="📚 فتح المرجع الشامل لكل المحاضرات", command=self.open_master_reference
        ).pack(fill="x", pady=(6, 0))
        ttk.Button(
            left_frame,
            text="🌐 فتح المرجع الشامل كصفحة منسقة (HTML)",
            command=self.open_master_reference_html,
        ).pack(fill="x", pady=(4, 0))

        # --- اللوحة الشمال: السجل + عرض الملخص ---
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)

        ttk.Label(right_frame, text="📝 محتوى الملخص / سجل العمليات", font=("Arial", 11, "bold")).pack(
            anchor="e"
        )
        self.output_box = scrolledtext.ScrolledText(right_frame, wrap="word", font=("Arial", 11))
        self.output_box.pack(fill="both", expand=True, pady=4)
        self.output_box.tag_configure("right", justify="right")

        self.status_var = tk.StringVar(value="جاهز.")
        ttk.Label(self.root, textvariable=self.status_var, anchor="e").pack(fill="x", padx=10, pady=(0, 6))

    # ------------------------------------------------------------ actions ---
    def add_files(self):
        paths = filedialog.askopenfilenames(title="اختر ملفات المحاضرات", filetypes=FILE_TYPES)
        for path in paths:
            default_name = os.path.splitext(os.path.basename(path))[0]
            lecture_name = simpledialog.askstring(
                "اسم المحاضرة", "اكتب اسم/عنوان المحاضرة:", initialvalue=default_name
            )
            if not lecture_name:
                lecture_name = default_name
            self.pending_files.append((lecture_name, path))
            self.pending_listbox.insert("end", f"{lecture_name}  ←  {os.path.basename(path)}")

    def process_all(self):
        if not self.pending_files:
            messagebox.showinfo("تنبيه", "مفيش ملفات مضافة للمعالجة.")
            return

        files_to_process = list(self.pending_files)
        self.pending_files.clear()
        self.pending_listbox.delete(0, "end")

        thread = threading.Thread(target=self._process_files_worker, args=(files_to_process,), daemon=True)
        thread.start()

    def _process_files_worker(self, files_to_process):
        model = self.model_name.get().strip() or ai_engine.DEFAULT_MODEL
        host = self.ollama_host.get().strip() or ai_engine.DEFAULT_OLLAMA_HOST

        for lecture_name, path in files_to_process:
            try:
                self.log_queue.put(("status", f"جاري معالجة: {lecture_name} ..."))

                def progress(msg, name=lecture_name):
                    self.log_queue.put(("status", f"[{name}] {msg}"))

                raw_text = extractors.extract_text(path, progress_callback=progress)
                summary = ai_engine.summarize_lecture(
                    raw_text, lecture_name, model=model, host=host, progress_callback=progress
                )
                knowledge_base.save_lecture_summary(lecture_name, path, summary)

                self.log_queue.put(("done_lecture", lecture_name))
                self.log_queue.put(("status", f"✅ تم الانتهاء من: {lecture_name}"))
            except Exception as e:
                self.log_queue.put(("error", f"❌ حصل خطأ أثناء معالجة '{lecture_name}':\n{e}"))

        self.log_queue.put(("status", "انتهت المعالجة لكل الملفات."))

    def _on_select_done_lecture(self, event):
        selection = self.done_listbox.curselection()
        if not selection:
            return
        lecture_name = self.done_listbox.get(selection[0])
        summary_path = knowledge_base.get_lecture_summary_path(lecture_name)
        if summary_path and os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.output_box.delete("1.0", "end")
            self.output_box.insert("end", content)

    def _on_open_done_lecture_html(self, event):
        """دبل كليك على محاضرة بيفتح نسختها المنسقة (HTML) في المتصفح مباشرة."""
        selection = self.done_listbox.curselection()
        if not selection:
            return
        lecture_name = self.done_listbox.get(selection[0])
        html_path = knowledge_base.get_lecture_summary_html_path(lecture_name)
        if html_path and os.path.exists(html_path):
            webbrowser.open(f"file://{os.path.abspath(html_path)}")
        else:
            messagebox.showwarning("تنبيه", "لا توجد نسخة HTML لهذه المحاضرة بعد.")

    def open_master_reference(self):
        path = knowledge_base.get_master_reference_path()
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", content)
        html_path = knowledge_base.get_master_reference_html_path()
        messagebox.showinfo(
            "المرجع الشامل",
            f"المرجع (Markdown) محفوظ في:\n{path}\n\n"
            f"النسخة المنسقة الجاهزة للنشر (HTML) محفوظة في:\n{html_path}",
        )

    def open_master_reference_html(self):
        html_path = knowledge_base.get_master_reference_html_path()
        webbrowser.open(f"file://{os.path.abspath(html_path)}")

    # ------------------------------------------------------------- misc ---
    def _refresh_lectures_list(self):
        self.done_listbox.delete(0, "end")
        for item in knowledge_base.get_all_lectures():
            self.done_listbox.insert("end", item["lecture_name"])

    def _poll_log_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "status":
                    self.status_var.set(payload)
                elif kind == "error":
                    self.status_var.set(payload.splitlines()[0])
                    messagebox.showerror("خطأ", payload)
                elif kind == "done_lecture":
                    self._refresh_lectures_list()
        except queue.Empty:
            pass
        finally:
            self.root.after(200, self._poll_log_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = LectureAIApp(root)
    root.mainloop()
