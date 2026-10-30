# -*- coding: utf-8 -*-
"""
SCAR RAR Uninstaller - Developed by scar development
Copyright (c) 2026 scar development. All Rights Reserved.
Clean Uninstaller for Windows (Settings > Installed Apps & Revo Uninstaller Compatible)
"""

import os
import sys
import time
import shutil
import tempfile
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw

try:
    import winreg
except ImportError:
    winreg = None

try:
    import ctypes
except ImportError:
    ctypes = None

# ==============================================================================
# 1. Self-Relaunch from %TEMP% (Crucial for deleting install directory on Windows)
# ==============================================================================
def check_self_relaunch():
    """إذا كان البرنامج يعمل من داخل مجلد التثبيت، ننسخه إلى %TEMP% ونعيد تشغيله لتحرير قفل الملفات وحذف المجلد بالكامل"""
    if "--run-uninstall" in sys.argv:
        return

    is_frozen = getattr(sys, "frozen", False)
    current_exe = os.path.abspath(sys.executable if is_frozen else __file__)
    current_dir = os.path.dirname(current_exe)
    temp_dir = tempfile.gettempdir()

    # إذا كنا لسنا داخل مجلد temp
    if not current_exe.lower().startswith(temp_dir.lower()):
        runner_name = "scarrar_uninstall_runner.exe" if is_frozen else "scarrar_uninstall_runner.py"
        temp_runner = os.path.join(temp_dir, runner_name)
        try:
            shutil.copy2(current_exe, temp_runner)
            # تمرير مجلد التثبيت كمعامل
            cmd_args = [temp_runner, "--run-uninstall", current_dir] + sys.argv[1:]
            if not is_frozen:
                cmd_args = [sys.executable] + cmd_args
            subprocess.Popen(cmd_args)
            sys.exit(0)
        except Exception:
            pass



# ==============================================================================
# 2. Translations (Arabic & English)
# ==============================================================================
TEXTS = {
    "English": {
        "title": "SCAR RAR Uninstaller - scar development",
        "header_title": "SCAR RAR Uninstallation",
        "header_subtitle": "Developed by scar development - 100% Clean Removal",
        "confirm_title": "Uninstall SCAR RAR",
        "confirm_prompt": "Are you sure you want to completely remove SCAR RAR and all of its components from your computer?",
        "confirm_details": (
            "This operation will cleanly remove:\n"
            "• All application binaries, libraries, and core compression engines\n"
            "• Windows Explorer cascading context menus and file associations\n"
            "• Desktop shortcuts and Start Menu entries\n"
            "• All registry registration keys and entries"
        ),
        "target_label": "Target Installation Folder:",
        "btn_uninstall": "Uninstall Now",
        "btn_cancel": "Cancel",
        "btn_finish": "Finish",
        "progress_title": "Removing SCAR RAR from your system...",
        "step_kill": "Closing any running instances of SCAR RAR...",
        "step_shortcuts": "Removing Desktop and Start Menu shortcuts...",
        "step_registry": "Cleaning Windows shell associations and context menus...",
        "step_files": "Deleting installed application files and components...",
        "step_done": "Uninstallation completed successfully!",
        "finish_title": "SCAR RAR Uninstalled Successfully",
        "finish_msg": (
            "SCAR RAR has been completely and cleanly removed from your computer.\n\n"
            "All components, context menus, and registry entries have been deleted.\n"
            "Thank you for using SCAR RAR by scar development."
        )
    },
    "العربية": {
        "title": "معالج إزالة تثبيت SCAR RAR - تطوير scar development",
        "header_title": "معالج إزالة تثبيت برنامج SCAR RAR",
        "header_subtitle": "تطوير وبرمجة scar development - إزالة نظيفة وشاملة 100%",
        "confirm_title": "إلغاء تثبيت برنامج SCAR RAR",
        "confirm_prompt": "هل أنت متأكد من رغبتك في إزالة برنامج SCAR RAR وكافة مكوناته وملفاته نهائياً من حاسوبك؟",
        "confirm_details": (
            "سيقوم هذا المعالج بتنظيف وحذف الآتي بالكامل:\n"
            "• كافة ملفات ومحركات البرنامج التنفيذية ومحركات الضغط الأساسية\n"
            "• قوائم الزر الأيمن المتشعبة في مستكشف ويندوز وارتباطات الأرشيف\n"
            "• اختصارات سطح المكتب ومجلد قائمة ابدأ (Start Menu)\n"
            "• سجلات التسجيل (Registry) الخاصة بتطبيقات ويندوز وRevo Uninstaller"
        ),
        "target_label": "مجلد تثبيت البرنامج المستهدف:",
        "btn_uninstall": "إزالة التثبيت الآن",
        "btn_cancel": "إلغاء",
        "btn_finish": "إنهاء",
        "progress_title": "جارٍ إزالة SCAR RAR وتنظيف النظام...",
        "step_kill": "إغلاق أي نوافذ نشطة لتطبيق SCAR RAR...",
        "step_shortcuts": "حذف اختصارات سطح المكتب وقائمة البرامج...",
        "step_registry": "تنظيف ارتباطات الملفات وقوائم السياق في الريجستري...",
        "step_files": "حذف ملفات البرنامج ومحرك الأرشيف...",
        "step_done": "اكتملت إزالة التثبيت بنجاح تام!",
        "finish_title": "تمت إزالة SCAR RAR بنجاح!",
        "finish_msg": (
            "تمت إزالة برنامج SCAR RAR وكافة ملفاته بنجاح تام من جهازك.\n\n"
            "تم تنظيف كافة السجلات والاختصارات وقوائم الويندوز بنسبة 100%.\n"
            "شكراً لاستخدامك برمجيات scar development."
        )
    }
}


# ==============================================================================
# 3. Icon Generator
# ==============================================================================
def create_uninstaller_icon():
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Shield shape
    pts = [(32, 4), (58, 14), (52, 44), (32, 60), (12, 44), (6, 14)]
    d.polygon(pts, fill="#0f172a", outline="#38bdf8", width=3)
    # Inner glow
    pts_in = [(32, 9), (53, 17), (48, 41), (32, 54), (16, 41), (11, 17)]
    d.polygon(pts_in, fill="#1e293b")
    # Red X for uninstaller
    d.line([(22, 22), (42, 42)], fill="#ef4444", width=5)
    d.line([(42, 22), (22, 42)], fill="#ef4444", width=5)
    return im


# ==============================================================================
# 4. Helper Registry Cleaner Function
# ==============================================================================
def delete_reg_key_tree(root, path):
    """حذف شجرة مفاتيح ريجستري كاملة مع كافة المفاتيح الفرعية بأمان"""
    if not winreg:
        return
    try:
        k = winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except Exception:
        return

    while True:
        try:
            sub = winreg.EnumKey(k, 0)
            delete_reg_key_tree(root, path + "\\" + sub)
        except OSError:
            break
    winreg.CloseKey(k)
    try:
        winreg.DeleteKey(root, path)
    except Exception:
        pass


def execute_full_uninstall(install_dir, callback_progress=None):
    """تنفيذ عملية الحذف الشاملة بنسبة 100%"""
    def log(pct, status):
        if callback_progress:
            callback_progress(pct, status)

    # 1. إنهاء العمليات المفتوحة لـ SCAR RAR
    log(15, "closing_proc")
    try:
        CREATE_NO_WINDOW = 0x08000000
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        subprocess.run(["taskkill", "/f", "/im", "SCAR RAR.exe"], capture_output=True, timeout=5, startupinfo=si, creationflags=CREATE_NO_WINDOW)
    except Exception:
        pass
    time.sleep(0.3)

    # 2. حذف الاختصارات من سطح المكتب وقائمة ابدأ
    log(35, "removing_shortcuts")
    # Desktop
    userprofile = os.environ.get("USERPROFILE", "")
    desktop_dirs = [
        os.path.join(userprofile, "Desktop"),
        os.path.join(userprofile, "OneDrive", "Bureau"),
        os.path.join(userprofile, "OneDrive", "Desktop"),
        os.path.join(os.environ.get("PUBLIC", ""), "Desktop")
    ]
    for d in desktop_dirs:
        lnk = os.path.join(d, "SCAR RAR.lnk")
        if os.path.exists(lnk):
            try:
                os.remove(lnk)
            except Exception:
                pass

    # Start Menu
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        start_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "SCAR RAR")
        if os.path.exists(start_dir):
            try:
                shutil.rmtree(start_dir, ignore_errors=True)
            except Exception:
                pass

    time.sleep(0.3)

    # 3. تنظيف ارتباطات الريجستري وقوائم السياق في ويندوز
    log(60, "cleaning_registry")
    if winreg:
        # أ) حذف مفتاح Uninstall الخاص بويندوز و Revo Uninstaller
        delete_reg_key_tree(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SCAR RAR")
        try:
            delete_reg_key_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SCAR RAR")
        except Exception:
            pass

        # ب) حذف قائمة السياق المتشعبة وارتباط ProgID
        delete_reg_key_tree(winreg.HKEY_CURRENT_USER, r"Software\Classes\SCAR_RAR_Archive")
        delete_reg_key_tree(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\SCARRAR")
        delete_reg_key_tree(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\SCARRAR")

        # ج) تنظيف الامتدادات من SystemFileAssociations واستعادة الوضع الأصلي
        exts = [".rar", ".zip", ".7z", ".iso", ".tar", ".gz", ".bz2", ".xz"]
        for ext in exts:
            delete_reg_key_tree(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\SCARRAR")
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{ext}", 0, winreg.KEY_READ | winreg.KEY_WRITE) as k:
                    val, _ = winreg.QueryValueEx(k, "")
                    if val == "SCAR_RAR_Archive":
                        winreg.DeleteValue(k, "")
            except Exception:
                pass

        # د) تحديث مستكشف ويندوز فوراً
        if ctypes:
            try:
                ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            except Exception:
                pass

    time.sleep(0.4)

    # 4. حذف مجلد التثبيت وكافة ملفات البرنامج
    log(85, "deleting_files")
    if install_dir and os.path.isdir(install_dir):
        # محاولة حذف الملفات أولاً ثم المجلد
        try:
            for root, dirs, files in os.walk(install_dir, topdown=False):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass
                for d in dirs:
                    try:
                        os.rmdir(os.path.join(root, d))
                    except Exception:
                        pass
            # حذف المجلد الرئيسي
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir, ignore_errors=True)
        except Exception:
            pass

    log(100, "done")
    time.sleep(0.4)


# ==============================================================================
# 5. Modern Uninstaller GUI Application
# ==============================================================================
class ScarUninstallerApp:
    def __init__(self, root: tk.Tk, target_dir: str):
        self.root = root
        self.target_dir = target_dir

        # كشف اللغة المفضلة (افتراض العربية أو الإنجليزية)
        self.current_lang = "العربية"
        # إذا كان هناك ملف إعدادات محفوظ
        settings_file = os.path.join(self.target_dir, "scarrar_settings.json")
        if os.path.exists(settings_file):
            try:
                import json
                with open(settings_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    saved_lang = cfg.get("language", "")
                    if "English" in saved_lang:
                        self.current_lang = "English"
            except Exception:
                pass

        self.root.title(self.t("title"))
        self.root.geometry("560x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#0c1017")
        self.center_window(560, 420)

        # تحسين شريط العنوان بالويندوز
        if ctypes:
            try:
                self.root.update_idletasks()
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
                border_color = ctypes.c_int(0x00221711)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border_color), 4)
            except Exception:
                pass

        # أيقونة النافذة
        self.icon_pil = create_uninstaller_icon()
        self.icon_tk = ImageTk.PhotoImage(self.icon_pil)
        try:
            self.root.iconphoto(False, self.icon_tk)
        except Exception:
            pass

        self.setup_styles()
        self.build_ui()
        self.show_confirm_screen()

    def t(self, key: str) -> str:
        lang_dict = TEXTS.get(self.current_lang, TEXTS["English"])
        return lang_dict.get(key, key)

    def center_window(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("ScarUninst.Horizontal.TProgressbar",
                        troughcolor="#0a0f1d",
                        background="#ef4444",
                        darkcolor="#ef4444",
                        lightcolor="#f87171",
                        bordercolor="#1e293b",
                        thickness=14)

    def build_ui(self):
        # 1. Header Frame
        self.header_frame = tk.Frame(self.root, bg="#101726", height=70, bd=0)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        hdr_inner = tk.Frame(self.header_frame, bg="#101726")
        hdr_inner.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_logo = tk.Label(hdr_inner, image=self.icon_tk, bg="#101726")
        self.lbl_logo.pack(side="left" if self.current_lang == "English" else "right", padx=10)

        hdr_texts = tk.Frame(hdr_inner, bg="#101726")
        hdr_texts.pack(side="left" if self.current_lang == "English" else "right", fill="both", expand=True)

        self.lbl_hdr_title = tk.Label(hdr_texts, text=self.t("header_title"),
                                      bg="#101726", fg="#ffffff", font=("Segoe UI", 12, "bold"),
                                      anchor="w" if self.current_lang == "English" else "e")
        self.lbl_hdr_title.pack(fill="x", pady=(2, 2))

        self.lbl_hdr_sub = tk.Label(hdr_texts, text=self.t("header_subtitle"),
                                    bg="#101726", fg="#38bdf8", font=("Segoe UI", 8),
                                    anchor="w" if self.current_lang == "English" else "e")
        self.lbl_hdr_sub.pack(fill="x")

        # الخط الفاصل أسفل الهيدر
        sep = tk.Frame(self.root, bg="#1e293b", height=1)
        sep.pack(side="top", fill="x")

        # 2. Bottom Button Bar
        self.btn_bar = tk.Frame(self.root, bg="#0a0e17", height=54)
        self.btn_bar.pack(side="bottom", fill="x")
        self.btn_bar.pack_propagate(False)

        btn_sep = tk.Frame(self.btn_bar, bg="#1e293b", height=1)
        btn_sep.pack(side="top", fill="x")

        self.btn_container = tk.Frame(self.btn_bar, bg="#0a0e17")
        self.btn_container.pack(fill="both", expand=True, padx=20, pady=8)

        # 3. Content Frame
        self.content_frame = tk.Frame(self.root, bg="#0c1017")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=14)

    def show_confirm_screen(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        for w in self.btn_container.winfo_children():
            w.destroy()

        # Confirm title
        tk.Label(self.content_frame, text=self.t("confirm_title"),
                 bg="#0c1017", fg="#f8fafc", font=("Segoe UI", 13, "bold"),
                 anchor="center", justify="center").pack(fill="x", pady=(0, 6))

        tk.Label(self.content_frame, text=self.t("confirm_prompt"),
                 bg="#0c1017", fg="#ef4444", font=("Segoe UI", 9, "bold"),
                 wraplength=500, justify="center").pack(fill="x", pady=(0, 10))

        # Card with details
        card = tk.Frame(self.content_frame, bg="#131a29", bd=1, relief="solid", highlightbackground="#1e293b")
        card.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(card, text=self.t("confirm_details"),
                 bg="#131a29", fg="#94a3b8", font=("Segoe UI", 9),
                 justify="left" if self.current_lang == "English" else "right",
                 anchor="nw", wraplength=480).pack(fill="both", expand=True, padx=14, pady=10)

        # Target directory display
        lbl_target = tk.Label(self.content_frame, text=f"{self.t('target_label')}  {self.target_dir}",
                              bg="#0c1017", fg="#64748b", font=("Segoe UI", 8),
                              anchor="w" if self.current_lang == "English" else "e")
        lbl_target.pack(fill="x")

        # Buttons
        btn_uninstall = tk.Button(self.btn_container, text=self.t("btn_uninstall"),
                                  command=self.start_uninstall,
                                  bg="#ef4444", fg="#ffffff", activebackground="#dc2626",
                                  activeforeground="#ffffff", font=("Segoe UI", 9, "bold"),
                                  relief="flat", width=16, height=1, cursor="hand2")
        btn_uninstall.pack(side="right" if self.current_lang == "English" else "left", padx=(6, 0))

        btn_cancel = tk.Button(self.btn_container, text=self.t("btn_cancel"),
                               command=self.root.destroy,
                               bg="#1e293b", fg="#94a3b8", activebackground="#334155",
                               activeforeground="#ffffff", font=("Segoe UI", 9),
                               relief="flat", width=12, height=1, cursor="hand2")
        btn_cancel.pack(side="right" if self.current_lang == "English" else "left")

    def start_uninstall(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        for w in self.btn_container.winfo_children():
            w.destroy()

        tk.Label(self.content_frame, text=self.t("progress_title"),
                 bg="#0c1017", fg="#38bdf8", font=("Segoe UI", 12, "bold"),
                 anchor="center").pack(fill="x", pady=(15, 12))

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.content_frame, style="ScarUninst.Horizontal.TProgressbar",
                                            orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 16))

        self.status_lbl = tk.Label(self.content_frame, text=self.t("step_kill"),
                                   bg="#0c1017", fg="#f8fafc", font=("Segoe UI", 9))
        self.status_lbl.pack(pady=4)

        # Run worker thread
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        def _cb(pct, status_code):
            text_map = {
                "closing_proc": self.t("step_kill"),
                "removing_shortcuts": self.t("step_shortcuts"),
                "cleaning_registry": self.t("step_registry"),
                "deleting_files": self.t("step_files"),
                "done": self.t("step_done")
            }
            txt = text_map.get(status_code, status_code)
            self.root.after(0, lambda: self._update_progress(pct, txt))

        execute_full_uninstall(self.target_dir, callback_progress=_cb)
        self.root.after(0, self.show_finished_screen)

    def _update_progress(self, pct, text):
        self.progress_bar["value"] = pct
        self.status_lbl.config(text=text)

    def show_finished_screen(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        for w in self.btn_container.winfo_children():
            w.destroy()

        tk.Label(self.content_frame, text=self.t("finish_title"),
                 bg="#0c1017", fg="#10b981", font=("Segoe UI", 14, "bold"),
                 anchor="center").pack(fill="x", pady=(20, 10))

        tk.Label(self.content_frame, text=self.t("finish_msg"),
                 bg="#0c1017", fg="#94a3b8", font=("Segoe UI", 9),
                 justify="center", wraplength=480).pack(fill="x", pady=10)

        btn_finish = tk.Button(self.btn_container, text=self.t("btn_finish"),
                               command=self._on_exit,
                               bg="#38bdf8", fg="#0c1017", activebackground="#0ea5e9",
                               activeforeground="#0c1017", font=("Segoe UI", 10, "bold"),
                               relief="flat", width=14, height=1, cursor="hand2")
        btn_finish.pack(side="right" if self.current_lang == "English" else "left")

    def _on_exit(self):
        self.root.destroy()
        # جدولة حذف الملف التنفيذي للملغي من مجلد temp بعد الخروج
        if getattr(sys, "frozen", False):
            temp_exe = os.path.abspath(sys.executable)
            if "temp" in temp_exe.lower():
                CREATE_NO_WINDOW = 0x08000000
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = 0
                cmd = f'cmd.exe /c ping 127.0.0.1 -n 2 > nul & del /f /q "{temp_exe}"'
                subprocess.Popen(cmd, startupinfo=si, creationflags=CREATE_NO_WINDOW)


# ==============================================================================
# 6. Entry Point
# ==============================================================================
def main():
    check_self_relaunch()
    target = None

    # استخراج مجلد التثبيت من الوسائط
    for idx, arg in enumerate(sys.argv):
        if arg == "--run-uninstall" and idx + 1 < len(sys.argv):
            target = sys.argv[idx + 1]
        elif arg.startswith("--target="):
            target = arg.split("=", 1)[1]

    # إذا لم يُمرر، نقرأه من الريجستري
    if not target or not os.path.exists(target):
        if winreg:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SCAR RAR", 0, winreg.KEY_READ) as k:
                    target, _ = winreg.QueryValueEx(k, "InstallLocation")
            except Exception:
                pass

    # إذا لم يوجد، نستخدم المسار الافتراضي
    if not target:
        default_base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        target = os.path.join(default_base, "Programs", "SCAR RAR")

    target = os.path.abspath(target)

    # وضع الحذف الصامت (Silent)
    if any(s in sys.argv for s in ["/SILENT", "/silent", "--silent", "-s", "/S"]):
        execute_full_uninstall(target)
        sys.exit(0)

    root = tk.Tk()
    app = ScarUninstallerApp(root, target)
    root.mainloop()

if __name__ == "__main__":
    main()
