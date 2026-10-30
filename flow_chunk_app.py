"""
================================================================================
FlowChunk Studio // Advanced Multi-Part Chunking & Reassembly Engine
المحاكي المتقدم لتقسيم الملفات، إدارة تدفق البيانات، والتحكم بالسرعة
================================================================================
"""

import os
import sys
import time
import zlib
import struct
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ==============================================================================
# 1. البروتوكول الثنائي لكتل البيانات (Binary Protocol Specification)
# ==============================================================================
MAGIC_HEADER = b"FLOW\x01\x00\x00\x00"  # التوقيع السحري: FLOW + الإصدار 1.0

# أعلام الترويسة القياسية
FLAG_EXTRA_PRESENT = 0x0001
FLAG_DATA_PRESENT  = 0x0002
FLAG_SPLIT_BEFORE  = 0x0008  # HFL_SPLITBEFORE: استكمال من الجزء السابق
FLAG_SPLIT_AFTER   = 0x0010  # HFL_SPLITAFTER: انقطاع واستمرار في الجزء اللاحق

class ChunkProtocol:
    @staticmethod
    def pack_header(filename: str, vol_num: int, chunk_size: int, total_size: int,
                    split_before: bool, split_after: bool, file_crc: int) -> bytes:
        flags = FLAG_DATA_PRESENT
        if split_before: flags |= FLAG_SPLIT_BEFORE
        if split_after:  flags |= FLAG_SPLIT_AFTER

        name_bytes = filename.encode('utf-8')
        name_len = len(name_bytes)

        # التعبئة الثنائية: Little-Endian
        # 8s: Magic (8)
        # H: Flags (2)
        # H: Volume Number (2)
        # Q: Chunk Data Size (8)
        # Q: Total Unpacked Size (8)
        # I: Global File CRC32 (4)
        # H: Name Length (2)
        header_body = struct.pack(
            "<8sHHQQIH",
            MAGIC_HEADER,
            flags,
            vol_num,
            chunk_size,
            total_size,
            file_crc,
            name_len
        ) + name_bytes

        # حساب CRC32 الخاص بالترويسة نفسها لمنع التلف
        header_crc = zlib.crc32(header_body) & 0xFFFFFFFF
        return header_body + struct.pack("<I", header_crc)

    @staticmethod
    def unpack_header(stream) -> dict:
        raw_fixed = stream.read(34)
        if len(raw_fixed) < 34:
            return None

        magic, flags, vol_num, chunk_size, total_size, file_crc, name_len = struct.unpack(
            "<8sHHQQIH", raw_fixed
        )

        if magic != MAGIC_HEADER:
            raise ValueError("توقيع الملف غير صالح أو الملف معطوب!")

        name_bytes = stream.read(name_len)
        if len(name_bytes) < name_len:
            raise ValueError("نهاية غير متوقعة لترويسة الملف أثناء قراءة الاسم.")

        raw_crc = stream.read(4)
        if len(raw_crc) < 4:
            raise ValueError("فقدان بايتات التحقق CRC32 للترويسة.")

        expected_crc = struct.unpack("<I", raw_crc)[0]
        actual_crc = zlib.crc32(raw_fixed + name_bytes) & 0xFFFFFFFF

        if expected_crc != actual_crc:
            raise ValueError("فشل فحص نزاهة الترويسة (Header CRC Mismatch)!")

        return {
            "flags": flags,
            "volume_number": vol_num,
            "chunk_size": chunk_size,
            "total_size": total_size,
            "file_crc": file_crc,
            "filename": name_bytes.decode('utf-8'),
            "is_split_before": bool(flags & FLAG_SPLIT_BEFORE),
            "is_split_after": bool(flags & FLAG_SPLIT_AFTER)
        }

# ==============================================================================
# 2. مسؤول التحكم بسرعة التدفق (Flow Rate Limiter)
# ==============================================================================
class RateLimiter:
    def __init__(self, limit_kbs: float = 0):
        self.set_limit(limit_kbs)
        self.start_time = time.time()
        self.total_bytes = 0

    def set_limit(self, limit_kbs: float):
        self.limit_bytes_per_sec = limit_kbs * 1024 if limit_kbs > 0 else 0
        self.start_time = time.time()
        self.total_bytes = 0

    def throttle(self, bytes_transferred: int):
        if self.limit_bytes_per_sec <= 0:
            return  # سرعة غير محدودة

        self.total_bytes += bytes_transferred
        elapsed = time.time() - self.start_time
        expected_time = self.total_bytes / self.limit_bytes_per_sec

        if expected_time > elapsed:
            time.sleep(expected_time - elapsed)

# ==============================================================================
# 3. محرك التقسيم والدمج (Core Chunking & Reassembly Engine)
# ==============================================================================
class FlowChunkEngine:
    @staticmethod
    def calculate_file_crc(file_path: str, progress_cb=None) -> int:
        crc = 0
        file_size = os.path.getsize(file_path)
        processed = 0
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024 * 1024):
                crc = zlib.crc32(chunk, crc)
                processed += len(chunk)
                if progress_cb:
                    progress_cb(processed, file_size)
        return crc & 0xFFFFFFFF

    @staticmethod
    def chunk_file(file_path: str, chunk_size_bytes: int, output_dir: str,
                   rate_limit_kbs: float, log_cb, progress_cb, stop_event: threading.Event):
        os.makedirs(output_dir, exist_ok=True)
        total_size = os.path.getsize(file_path)
        base_name = os.path.basename(file_path)

        log_cb(f"🚀 بدء عملية فحص وحساب التوقيع الشامل للملف: {base_name}")
        file_crc = FlowChunkEngine.calculate_file_crc(file_path)
        log_cb(f"🛡️ التوقيع الشامل (Global CRC32): 0x{file_crc:08X}")

        rate_limiter = RateLimiter(rate_limit_kbs)
        total_parts = (total_size + chunk_size_bytes - 1) // chunk_size_bytes
        bytes_transferred = 0

        with open(file_path, 'rb') as src:
            for vol_idx in range(1, total_parts + 1):
                if stop_event.is_set():
                    log_cb("⚠️ تم إيقاف عملية التقسيم يدوياً من قبل المستخدم.")
                    return False

                remaining = total_size - bytes_transferred
                current_chunk_size = min(remaining, chunk_size_bytes)

                split_before = (vol_idx > 1)
                split_after  = (vol_idx < total_parts)

                header = ChunkProtocol.pack_header(
                    filename=base_name,
                    vol_num=vol_idx,
                    chunk_size=current_chunk_size,
                    total_size=total_size,
                    split_before=split_before,
                    split_after=split_after,
                    file_crc=file_crc
                )

                part_filename = f"{base_name}.part{vol_idx:02d}.flow"
                part_path = os.path.join(output_dir, part_filename)

                log_cb(f"📦 [الجزء {vol_idx}/{total_parts}] كتابة: {part_filename} (الحجم: {current_chunk_size:,} بايت) | SplitBefore: {split_before} | SplitAfter: {split_after}")

                with open(part_path, 'wb') as dst:
                    dst.write(header)
                    read_remaining = current_chunk_size
                    buffer_size = 64 * 1024  # 64 KB per step

                    while read_remaining > 0:
                        if stop_event.is_set():
                            log_cb("⚠️ إيقاف فوري للتدفق.")
                            return False

                        to_read = min(read_remaining, buffer_size)
                        buf = src.read(to_read)
                        if not buf:
                            break

                        dst.write(buf)
                        read_remaining -= len(buf)
                        bytes_transferred += len(buf)

                        rate_limiter.throttle(len(buf))
                        if progress_cb:
                            progress_cb(bytes_transferred, total_size, vol_idx, total_parts)

        log_cb(f"✅ اكتمل تقسيم وتوليد {total_parts} أجزاء بنجاح وبأعلى معايير النزاهة.")
        return True

    @staticmethod
    def reassemble_file(first_part_path: str, output_dir: str, rate_limit_kbs: float,
                         log_cb, progress_cb, stop_event: threading.Event):
        os.makedirs(output_dir, exist_ok=True)
        # التحقق من الجزء الأول
        if not os.path.exists(first_part_path):
            raise FileNotFoundError("لم يتم العثور على الجزء المحدد!")

        dir_name = os.path.dirname(first_part_path)
        base_file_name = os.path.basename(first_part_path)

        # استخراج اسم النمط الأساسي (Base pattern)
        import re
        match = re.search(r"^(.*?)\.part(\d+)\.flow$", base_file_name, re.IGNORECASE)
        if not match:
            raise ValueError("تسمية الملف لا تتبع نمط الأجزاء القياسي (*.part01.flow)!")

        core_name = match.group(1)
        current_vol = 1
        rate_limiter = RateLimiter(rate_limit_kbs)

        temp_output_path = None
        final_output_path = None
        rolling_crc = 0
        total_accumulated = 0
        expected_total_size = 0
        expected_global_crc = 0

        try:
            while True:
                if stop_event.is_set():
                    log_cb("⚠️ تم إلغاء عملية الدمج.")
                    if temp_output_path and os.path.exists(temp_output_path):
                        os.remove(temp_output_path)
                    return False

                part_file_path = os.path.join(dir_name, f"{core_name}.part{current_vol:02d}.flow")
                if not os.path.exists(part_file_path):
                    raise FileNotFoundError(f"الجزء المتسلسل مفقود: {part_file_path}")

                log_cb(f"🔍 [مسؤول المدخلات] فتح وفحص الجزء {current_vol}: {os.path.basename(part_file_path)}")

                with open(part_file_path, 'rb') as part_f:
                    header = ChunkProtocol.unpack_header(part_f)
                    if not header:
                        raise ValueError(f"تعذر قراءة الترويسة في الجزء {current_vol}!")

                    if current_vol == 1:
                        expected_total_size = header["total_size"]
                        expected_global_crc = header["file_crc"]
                        final_output_path = os.path.join(output_dir, header["filename"])
                        temp_output_path = os.path.join(output_dir, f"{header['filename']}.flow_tmp")
                        log_cb(f"📄 استكشاف الملف الأصلي: {header['filename']} (الحجم الإجمالي: {expected_total_size:,} بايت)")
                        out_f = open(temp_output_path, 'wb')
                    else:
                        out_f = open(temp_output_path, 'ab')

                    chunk_remaining = header["chunk_size"]
                    buffer_size = 64 * 1024

                    with out_f:
                        while chunk_remaining > 0:
                            if stop_event.is_set():
                                return False
                            to_read = min(chunk_remaining, buffer_size)
                            buf = part_f.read(to_read)
                            if not buf:
                                raise ValueError(f"انقطاع غير متوقع للبيانات في الجزء {current_vol}!")

                            out_f.write(buf)
                            rolling_crc = zlib.crc32(buf, rolling_crc)
                            chunk_remaining -= len(buf)
                            total_accumulated += len(buf)

                            rate_limiter.throttle(len(buf))
                            if progress_cb:
                                progress_cb(total_accumulated, expected_total_size, current_vol, -1)

                    if not header["is_split_after"]:
                        log_cb(f"🏁 تم الوصول إلى الجزء الأخير بنجاح ({current_vol}).")
                        break

                    current_vol += 1

            # الفحص النهائي للنزاهة
            final_crc = rolling_crc & 0xFFFFFFFF
            log_cb(f"📊 التحقق النهائي: التوقيع المحسوب 0x{final_crc:08X} مقابل المتوقع 0x{expected_global_crc:08X}")

            if final_crc != expected_global_crc or total_accumulated != expected_total_size:
                raise ValueError("فشل فحص النزاهة الشامل! البيانات ملوثة أو فقدت بايتات أثناء النقل.")

            # الالتزام الذري: تحويل الملف المؤقت إلى النهائي
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
            os.rename(temp_output_path, final_output_path)

            log_cb(f"✨ اكتمل دمج الملف بنجاح وتطابق تام 100%: {final_output_path}")
            return True

        except Exception as e:
            if temp_output_path and os.path.exists(temp_output_path):
                try: os.remove(temp_output_path)
                except: pass
            raise e

# ==============================================================================
# 4. واجهة المستخدم الرسومية الحديثة (Modern Frameless Window GUI)
# ==============================================================================
class FramelessApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FlowChunk Studio")
        self.root.geometry("860x640")
        self.root.configure(bg="#0d1117")

        # تفعيل نمط النافذة بدون إطار خارجي (Frameless Window)
        self.root.overrideredirect(True)

        # ضبط المحاذاة في وسط الشاشة
        self.center_window(860, 640)

        # المتغيرات الخاصة بالتشغيل والتحكم
        self.stop_event = threading.Event()
        self.active_thread = None

        self._offset_x = 0
        self._offset_y = 0

        self.setup_styles()
        self.create_title_bar()
        self.create_body()

    def center_window(self, width, height):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # ألوان النمط الداكن العصري
        style.configure("Dark.TNotebook", background="#0d1117", borderwidth=0)
        style.configure("Dark.TNotebook.Tab", background="#161b22", foreground="#c9d1d9",
                        font=("Segoe UI", 10, "bold"), padding=[20, 8], borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", "#1f6feb")],
                  foreground=[("selected", "#ffffff")])

        style.configure("Modern.Horizontal.TProgressbar",
                        background="#238636", troughcolor="#161b22",
                        borderwidth=0, thickness=12)

    # --------------------------------------------------------------------------
    # شريط العنوان المخصص القابل للسحب (Custom Draggable Title Bar)
    # --------------------------------------------------------------------------
    def create_title_bar(self):
        self.title_bar = tk.Frame(self.root, bg="#161b22", height=38)
        self.title_bar.pack(side="top", fill="x")
        self.title_bar.pack_propagate(False)

        # ربط أحداث تحريك النافذة
        self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)

        # شعار وعنوان التطبيق
        title_label = tk.Label(
            self.title_bar,
            text="⚡ FLOWCHUNK STUDIO // ARCHIVE ENGINE & RATE ARBITER",
            bg="#161b22", fg="#58a6ff",
            font=("Segoe UI", 10, "bold")
        )
        title_label.pack(side="left", padx=15)
        title_label.bind("<ButtonPress-1>", self.start_drag)
        title_label.bind("<B1-Motion>", self.do_drag)

        # أزرار الإغلاق والتصغير
        btn_close = tk.Label(
            self.title_bar, text="✕", bg="#161b22", fg="#8b949e",
            font=("Segoe UI", 11, "bold"), width=4
        )
        btn_close.pack(side="right", fill="y")
        btn_close.bind("<Button-1>", lambda e: self.root.destroy())
        btn_close.bind("<Enter>", lambda e: btn_close.configure(bg="#da3633", fg="#ffffff"))
        btn_close.bind("<Leave>", lambda e: btn_close.configure(bg="#161b22", fg="#8b949e"))

        btn_min = tk.Label(
            self.title_bar, text="—", bg="#161b22", fg="#8b949e",
            font=("Segoe UI", 10, "bold"), width=4
        )
        btn_min.pack(side="right", fill="y")
        btn_min.bind("<Button-1>", self.minimize_window)
        btn_min.bind("<Enter>", lambda e: btn_min.configure(bg="#30363d", fg="#ffffff"))
        btn_min.bind("<Leave>", lambda e: btn_min.configure(bg="#161b22", fg="#8b949e"))

    def start_drag(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self, event):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.bind("<FocusIn>", self.on_focus_in)

    def on_focus_in(self, event):
        if self.root.state() == "normal":
            self.root.overrideredirect(True)
            self.root.unbind("<FocusIn>")

    # --------------------------------------------------------------------------
    # هيكل التطبيق والتبويبات
    # --------------------------------------------------------------------------
    def create_body(self):
        main_frame = tk.Frame(self.root, bg="#0d1117")
        main_frame.pack(fill="both", expand=True, padx=16, pady=12)

        self.notebook = ttk.Notebook(main_frame, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # التبويب 1: تقسيم وتدفق الملفات
        self.tab_chunk = tk.Frame(self.notebook, bg="#0d1117")
        self.notebook.add(self.tab_chunk, text="  تقسيم وتوزيع التدفق (Chunking)  ")
        self.build_chunk_tab()

        # التبويب 2: دمج واستعادة الأجزاء
        self.tab_assemble = tk.Frame(self.notebook, bg="#0d1117")
        self.notebook.add(self.tab_assemble, text="  دمج واستعادة الأجزاء (Reassemble)  ")
        self.build_assemble_tab()

        # لوحة السجل التفاعلي في الأسفل
        log_frame = tk.LabelFrame(main_frame, text=" سجل العمليات ومراقبة التدفق الحي (Live Telemetry) ",
                                  bg="#0d1117", fg="#58a6ff", font=("Segoe UI", 9, "bold"))
        log_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.log_text = tk.Text(log_frame, bg="#010409", fg="#7ee787",
                                font=("Consolas", 9), height=8, borderwidth=0, padx=8, pady=6)
        self.log_text.pack(fill="both", expand=True, side="left")

        scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scroll.set)

    def log(self, message: str):
        def _append():
            ts = time.strftime("[%H:%M:%S] ")
            self.log_text.insert(tk.END, ts + message + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, _append)

    # --------------------------------------------------------------------------
    # محتويات تبويب التقسيم (Chunk Tab)
    # --------------------------------------------------------------------------
    def build_chunk_tab(self):
        panel = tk.Frame(self.tab_chunk, bg="#0d1117")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. اختيار الملف
        f1 = tk.Frame(panel, bg="#0d1117")
        f1.pack(fill="x", pady=6)
        tk.Label(f1, text="الملف المستهدف:", bg="#0d1117", fg="#c9d1d9",
                 font=("Segoe UI", 9, "bold"), width=16, anchor="w").pack(side="left")
        self.chunk_file_entry = tk.Entry(f1, bg="#161b22", fg="#ffffff",
                                         insertbackground="white", font=("Segoe UI", 9))
        self.chunk_file_entry.pack(side="left", fill="x", expand=True, padx=6)
        btn_b = tk.Button(f1, text="استعراض...", bg="#21262d", fg="#c9d1d9",
                          activebackground="#30363d", activeforeground="white",
                          command=self.browse_chunk_file)
        btn_b.pack(side="left")

        # 2. تحديد حجم الجزء
        f2 = tk.Frame(panel, bg="#0d1117")
        f2.pack(fill="x", pady=6)
        tk.Label(f2, text="حجم الجزء (Chunk):", bg="#0d1117", fg="#c9d1d9",
                 font=("Segoe UI", 9, "bold"), width=16, anchor="w").pack(side="left")

        self.chunk_size_var = tk.StringVar(value="5 MB")
        chunk_options = ["500 KB", "1 MB", "2 MB", "5 MB", "10 MB", "25 MB", "50 MB", "100 MB"]
        cb = ttk.Combobox(f2, textvariable=self.chunk_size_var, values=chunk_options, state="readonly", width=12)
        cb.pack(side="left", padx=6)

        # 3. ميزة تحديد السرعة اليدوية (Manual Flow Rate Limiter)
        f3 = tk.Frame(panel, bg="#161b22", relief="flat", bd=1)
        f3.pack(fill="x", pady=10, ipady=6, ipadx=8)

        tk.Label(f3, text="⚡ محدد سرعة التدفق (Rate Limiter):", bg="#161b22", fg="#f0883e",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=6)

        self.rate_scale_var = tk.DoubleVar(value=0)
        self.rate_label_var = tk.StringVar(value="غير محدود (Max Speed)")

        scale = tk.Scale(f3, from_=0, to=20480, orient="horizontal", variable=self.rate_scale_var,
                         bg="#161b22", fg="#8b949e", highlightthickness=0, length=240,
                         showvalue=False, command=self.on_rate_slider_change)
        scale.pack(side="left", padx=10)

        tk.Label(f3, textvariable=self.rate_label_var, bg="#161b22", fg="#58a6ff",
                 font=("Segoe UI", 9, "bold"), width=22, anchor="w").pack(side="left")

        # 4. شريط التقدم وزر البدء
        self.chunk_prog = ttk.Progressbar(panel, style="Modern.Horizontal.TProgressbar", mode="determinate")
        self.chunk_prog.pack(fill="x", pady=(10, 4))

        self.chunk_status_lbl = tk.Label(panel, text="جاهز للبدء", bg="#0d1117", fg="#8b949e", font=("Segoe UI", 9))
        self.chunk_status_lbl.pack(anchor="w")

        btn_box = tk.Frame(panel, bg="#0d1117")
        btn_box.pack(fill="x", pady=8)

        self.btn_chunk_start = tk.Button(btn_box, text="▶ بدء عملية التقسيم والتدفق",
                                         bg="#238636", fg="#ffffff", activebackground="#2ea043",
                                         font=("Segoe UI", 10, "bold"), padx=15, pady=4,
                                         command=self.start_chunking)
        self.btn_chunk_start.pack(side="left")

        self.btn_chunk_stop = tk.Button(btn_box, text="⏹ إلغاء",
                                        bg="#da3633", fg="#ffffff", activebackground="#f85149",
                                        font=("Segoe UI", 10, "bold"), padx=15, pady=4,
                                        state="disabled", command=self.stop_operation)
        self.btn_chunk_stop.pack(side="left", padx=8)

    def on_rate_slider_change(self, val):
        v = float(val)
        if v == 0:
            self.rate_label_var.set("غير محدود (Max Speed)")
        elif v < 1024:
            self.rate_label_var.set(f"{int(v)} KB/s")
        else:
            self.rate_label_var.set(f"{v/1024:.2f} MB/s")

    def browse_chunk_file(self):
        f = filedialog.askopenfilename(title="اختر الملف المراد تقسيمه")
        if f:
            self.chunk_file_entry.delete(0, tk.END)
            self.chunk_file_entry.insert(0, f)

    def parse_chunk_size(self) -> int:
        s = self.chunk_size_var.get().upper()
        if "KB" in s:
            return int(s.replace("KB", "").strip()) * 1024
        elif "MB" in s:
            return int(s.replace("MB", "").strip()) * 1024 * 1024
        return 5 * 1024 * 1024

    def start_chunking(self):
        file_path = self.chunk_file_entry.get().strip()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("خطأ", "يرجى اختيار ملف صالح أولاً!")
            return

        chunk_size = self.parse_chunk_size()
        rate_kbs = self.rate_scale_var.get()
        out_dir = os.path.dirname(file_path)

        self.stop_event.clear()
        self.btn_chunk_start.configure(state="disabled")
        self.btn_chunk_stop.configure(state="normal")
        self.chunk_prog["value"] = 0

        def _worker():
            try:
                def _prog(curr, total, vol, max_vol):
                    pct = (curr / total) * 100
                    self.root.after(0, lambda: self.chunk_prog.configure(value=pct))
                    self.root.after(0, lambda: self.chunk_status_lbl.configure(
                        text=f"جاري المعالجة: {pct:.1f}% | الجزء الحالي: {vol}/{max_vol} | المنقول: {curr/(1024*1024):.2f} MB من {total/(1024*1024):.2f} MB"
                    ))

                FlowChunkEngine.chunk_file(
                    file_path=file_path,
                    chunk_size_bytes=chunk_size,
                    output_dir=out_dir,
                    rate_limit_kbs=rate_kbs,
                    log_cb=self.log,
                    progress_cb=_prog,
                    stop_event=self.stop_event
                )
            except Exception as e:
                self.log(f"❌ خطأ أثناء التقسيم: {str(e)}")
            finally:
                self.root.after(0, lambda: self.btn_chunk_start.configure(state="normal"))
                self.root.after(0, lambda: self.btn_chunk_stop.configure(state="disabled"))
                self.root.after(0, lambda: self.chunk_status_lbl.configure(text="اكتملت العملية."))

        self.active_thread = threading.Thread(target=_worker, daemon=True)
        self.active_thread.start()

    # --------------------------------------------------------------------------
    # محتويات تبويب الدمج (Reassemble Tab)
    # --------------------------------------------------------------------------
    def build_assemble_tab(self):
        panel = tk.Frame(self.tab_assemble, bg="#0d1117")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. اختيار الجزء الأول
        f1 = tk.Frame(panel, bg="#0d1117")
        f1.pack(fill="x", pady=6)
        tk.Label(f1, text="الجزء الأول (.part01):", bg="#0d1117", fg="#c9d1d9",
                 font=("Segoe UI", 9, "bold"), width=18, anchor="w").pack(side="left")
        self.part1_entry = tk.Entry(f1, bg="#161b22", fg="#ffffff",
                                    insertbackground="white", font=("Segoe UI", 9))
        self.part1_entry.pack(side="left", fill="x", expand=True, padx=6)
        btn_b = tk.Button(f1, text="استعراض...", bg="#21262d", fg="#c9d1d9",
                          activebackground="#30363d", activeforeground="white",
                          command=self.browse_part1_file)
        btn_b.pack(side="left")

        # 2. مجلد الإخراج
        f2 = tk.Frame(panel, bg="#0d1117")
        f2.pack(fill="x", pady=6)
        tk.Label(f2, text="مجلد حفظ الملف النهائي:", bg="#0d1117", fg="#c9d1d9",
                 font=("Segoe UI", 9, "bold"), width=18, anchor="w").pack(side="left")
        self.out_dir_entry = tk.Entry(f2, bg="#161b22", fg="#ffffff",
                                      insertbackground="white", font=("Segoe UI", 9))
        self.out_dir_entry.pack(side="left", fill="x", expand=True, padx=6)
        btn_out = tk.Button(f2, text="تحديد...", bg="#21262d", fg="#c9d1d9",
                            activebackground="#30363d", activeforeground="white",
                            command=self.browse_out_dir)
        btn_out.pack(side="left")

        # 3. شريط التقدم والأزرار
        self.asmb_prog = ttk.Progressbar(panel, style="Modern.Horizontal.TProgressbar", mode="determinate")
        self.asmb_prog.pack(fill="x", pady=(14, 4))

        self.asmb_status_lbl = tk.Label(panel, text="جاهز للدمج واستعادة الملف", bg="#0d1117", fg="#8b949e", font=("Segoe UI", 9))
        self.asmb_status_lbl.pack(anchor="w")

        btn_box = tk.Frame(panel, bg="#0d1117")
        btn_box.pack(fill="x", pady=8)

        self.btn_asmb_start = tk.Button(btn_box, text="⚡ دمج واستعادة الملف الأصلي",
                                        bg="#1f6feb", fg="#ffffff", activebackground="#388bfd",
                                        font=("Segoe UI", 10, "bold"), padx=15, pady=4,
                                        command=self.start_reassemble)
        self.btn_asmb_start.pack(side="left")

        self.btn_asmb_stop = tk.Button(btn_box, text="⏹ إلغاء",
                                       bg="#da3633", fg="#ffffff", activebackground="#f85149",
                                       font=("Segoe UI", 10, "bold"), padx=15, pady=4,
                                       state="disabled", command=self.stop_operation)
        self.btn_asmb_stop.pack(side="left", padx=8)

    def browse_part1_file(self):
        f = filedialog.askopenfilename(
            title="اختر الجزء الأول",
            filetypes=[("Flow Parts", "*.part01.flow"), ("All Files", "*.*")]
        )
        if f:
            self.part1_entry.delete(0, tk.END)
            self.part1_entry.insert(0, f)
            if not self.out_dir_entry.get().strip():
                self.out_dir_entry.insert(0, os.path.dirname(f))

    def browse_out_dir(self):
        d = filedialog.askdirectory(title="اختر مجلد الإخراج")
        if d:
            self.out_dir_entry.delete(0, tk.END)
            self.out_dir_entry.insert(0, d)

    def start_reassemble(self):
        p1 = self.part1_entry.get().strip()
        out_d = self.out_dir_entry.get().strip()
        if not p1 or not os.path.exists(p1):
            messagebox.showerror("خطأ", "يرجى تحديد الجزء الأول (.part01.flow) بشكل صحيح!")
            return
        if not out_d or not os.path.isdir(out_d):
            messagebox.showerror("خطأ", "يرجى تحديد مجلد إخراج صالح!")
            return

        rate_kbs = self.rate_scale_var.get()
        self.stop_event.clear()
        self.btn_asmb_start.configure(state="disabled")
        self.btn_asmb_stop.configure(state="normal")
        self.asmb_prog["value"] = 0

        def _worker():
            try:
                def _prog(curr, total, vol, _):
                    pct = (curr / total) * 100
                    self.root.after(0, lambda: self.asmb_prog.configure(value=pct))
                    self.root.after(0, lambda: self.asmb_status_lbl.configure(
                        text=f"جاري الدمج: {pct:.1f}% | استيعاب الجزء: {vol} | المدمج: {curr/(1024*1024):.2f} MB"
                    ))

                FlowChunkEngine.reassemble_file(
                    first_part_path=p1,
                    output_dir=out_d,
                    rate_limit_kbs=rate_kbs,
                    log_cb=self.log,
                    progress_cb=_prog,
                    stop_event=self.stop_event
                )
            except Exception as e:
                self.log(f"❌ فشل الدمج: {str(e)}")
            finally:
                self.root.after(0, lambda: self.btn_asmb_start.configure(state="normal"))
                self.root.after(0, lambda: self.btn_asmb_stop.configure(state="disabled"))
                self.root.after(0, lambda: self.asmb_status_lbl.configure(text="اكتملت عملية الاستعادة."))

        self.active_thread = threading.Thread(target=_worker, daemon=True)
        self.active_thread.start()

    def stop_operation(self):
        self.stop_event.set()
        self.log("🛑 جاري إرسال إشارة الإيقاف الفوري لخط الأنابيب...")

# ==============================================================================
# نقطة الدخول الرئيسية للبرنامج (Application Entry Point)
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = FramelessApp(root)
    root.mainloop()
