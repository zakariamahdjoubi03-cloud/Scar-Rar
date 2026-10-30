import os



import sys



import json



import time



import shutil



import ctypes



import subprocess



import threading



import tkinter as tk



from tkinter import ttk, filedialog, messagebox



from PIL import Image, ImageTk, ImageDraw

try:
    import winreg
except ImportError:
    winreg = None

CURRENT_INSTALLER_VERSION = "1.0.3"

def apply_window_icon(win, app_or_ico=None):
    if not win:
        return
    ico_candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "scarrar_icon.ico"),
        os.path.join(os.getcwd(), "scarrar_icon.ico"),
    ]
    if getattr(sys, "frozen", False):
        ico_candidates.insert(0, os.path.join(os.path.dirname(sys.executable), "scarrar_icon.ico"))
    for p in ico_candidates:
        if os.path.exists(p):
            try:
                win.iconbitmap(p)
                return
            except Exception:
                pass

class ScarMessageDialog:
    def __init__(self, parent, title, message, dialog_type="info", buttons=("OK",), default_idx=0):
        self.parent = parent
        self.result = None
        self.buttons = buttons

        if not parent:
            self.win = tk.Toplevel()
        else:
            self.win = tk.Toplevel(parent)

        self.win.title(title)
        self.win.configure(bg="#0c1017")
        self.win.resizable(False, False)

        apply_window_icon(self.win, parent)

        try:
            self.win.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

        if parent and hasattr(parent, "winfo_viewable") and parent.winfo_viewable():
            try:
                self.win.transient(parent)
            except Exception:
                pass
        self.win.grab_set()

        # Dialog builds its own vector icons in _create_dialog_icon

        self._build_ui(message, dialog_type)
        self._center(440, 160)

        self.win.bind("<Return>", lambda e: self._on_button_click(buttons[default_idx]))
        self.win.bind("<Escape>", lambda e: self._on_button_click(buttons[-1]))
        self.win.protocol("WM_DELETE_WINDOW", lambda: self._on_button_click(buttons[-1]))

        self.win.wait_window()

    def _create_dialog_icon(self, dialog_type):
        im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)

        if dialog_type == "question":
            d.ellipse([2, 2, 42, 42], fill="#0284c7", outline="#38bdf8", width=1)
            d.arc([14, 9, 30, 23], start=180, end=360, fill="#ffffff", width=4)
            d.line([(30, 16), (22, 24), (22, 28)], fill="#ffffff", width=4)
            d.ellipse([20, 32, 24, 36], fill="#ffffff")
        elif dialog_type == "warning":
            pts = [(22, 3), (42, 41), (2, 41)]
            d.polygon(pts, fill="#f59e0b", outline="#fbbf24", width=1)
            d.line([(22, 16), (22, 29)], fill="#0c1017", width=4)
            d.ellipse([20, 33, 24, 37], fill="#0c1017")
        elif dialog_type == "error":
            d.ellipse([2, 2, 42, 42], fill="#ef4444", outline="#f87171", width=1)
            d.line([(13, 13), (31, 31)], fill="#ffffff", width=4)
            d.line([(31, 13), (13, 31)], fill="#ffffff", width=4)
        else: # info
            d.ellipse([2, 2, 42, 42], fill="#0284c7", outline="#38bdf8", width=1)
            d.ellipse([20, 10, 24, 14], fill="#ffffff")
            d.line([(22, 19), (22, 33)], fill="#ffffff", width=4)
            d.line([(18, 19), (22, 19)], fill="#ffffff", width=3)
            d.line([(18, 33), (26, 33)], fill="#ffffff", width=3)

        return ImageTk.PhotoImage(im)

    def _build_ui(self, message, dialog_type):
        card = tk.Frame(self.win, bg="#0c1017", bd=0, highlightbackground="#1e293b", highlightthickness=1)
        card.pack(fill="both", expand=True)

        content_frame = tk.Frame(card, bg="#0c1017", padx=16, pady=16)
        content_frame.pack(fill="both", expand=True)

        self._icon_img = self._create_dialog_icon(dialog_type)
        lbl_icon = tk.Label(content_frame, image=self._icon_img, bg="#0c1017")
        lbl_icon.pack(side="left", anchor="n", padx=(0, 14))

        lbl_msg = tk.Label(
            content_frame,
            text=message,
            bg="#0c1017",
            fg="#f8fafc",
            font=("Segoe UI", 10),
            wraplength=340,
            justify="left",
            anchor="w"
        )
        lbl_msg.pack(side="left", fill="both", expand=True)

        btn_bar = tk.Frame(card, bg="#111722", padx=16, pady=10, highlightbackground="#1e293b", highlightthickness=1)
        btn_bar.pack(side="bottom", fill="x")

        for idx, btn_text in enumerate(reversed(self.buttons)):
            is_primary = (btn_text in ("Yes", "OK", "موافق", "نعم"))
            bg_col = "#0066cc" if is_primary else "#1e293b"
            fg_col = "#ffffff" if is_primary else "#f8fafc"
            hover_bg = "#0052a3" if is_primary else "#334155"

            btn = tk.Button(
                btn_bar,
                text=btn_text,
                bg=bg_col,
                fg=fg_col,
                activebackground=hover_bg,
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                width=10,
                height=1,
                cursor="hand2",
                font=("Segoe UI", 9, "bold" if is_primary else "normal"),
                command=lambda b=btn_text: self._on_button_click(b)
            )
            btn.pack(side="right", padx=(8, 0))

    def _on_button_click(self, btn_text):
        self.result = btn_text
        self.win.destroy()

    def _center(self, w, h):
        try:
            self.win.update_idletasks()
            sw = self.win.winfo_screenwidth()
            sh = self.win.winfo_screenheight()
            if self.parent and hasattr(self.parent, "winfo_viewable") and self.parent.winfo_viewable() and self.parent.winfo_width() > 100:
                px = self.parent.winfo_rootx()
                py = self.parent.winfo_rooty()
                pw = self.parent.winfo_width()
                ph = self.parent.winfo_height()
                x = px + (pw - w) // 2
                y = py + (ph - h) // 2
            else:
                x = (sw - w) // 2
                y = (sh - h) // 2
            self.win.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

def scar_showinfo(title, message, parent=None):
    ScarMessageDialog(parent, title, message, dialog_type="info", buttons=("OK",))
    return "ok"

def scar_askyesno(title, message, parent=None):
    dlg = ScarMessageDialog(parent, title, message, dialog_type="question", buttons=("Yes", "No"))
    return dlg.result == "Yes"

def scar_askokcancel(title, message, parent=None):
    dlg = ScarMessageDialog(parent, title, message, dialog_type="question", buttons=("OK", "Cancel"))
    return dlg.result == "OK"

def scar_showwarning(title, message, parent=None):
    ScarMessageDialog(parent, title, message, dialog_type="warning", buttons=("OK",))
    return "ok"

def scar_showerror(title, message, parent=None):
    ScarMessageDialog(parent, title, message, dialog_type="error", buttons=("OK",))
    return "ok"

class ScarMessageBoxProxy:
    showinfo = staticmethod(scar_showinfo)
    askyesno = staticmethod(scar_askyesno)
    askokcancel = staticmethod(scar_askokcancel)
    showwarning = staticmethod(scar_showwarning)
    showerror = staticmethod(scar_showerror)

messagebox = ScarMessageBoxProxy()







# ==============================================================================



# نصوص التثبيت متعددة اللغات (100% لغة نقية بدون خلط)



# ==============================================================================



INSTALLER_I18N = {



    "English": {



        "title": "SCAR RAR Setup - scar development",



        "header_title": "SCAR RAR Installation Wizard",



        "header_subtitle": "High-Performance Compression & Archiving Engine",



        "step_lang": "Language Selection",



        "step_license": "End User License Agreement & Proprietary Rights",



        "step_dir": "Destination Folder & Setup Options",



        "step_install": "Installing SCAR RAR",



        "step_finish": "Completing Setup",



        "lang_prompt": "Choose the default interface language for SCAR RAR:",



        "lang_desc": "This language will be applied to both this installer and your installed application.",



        "license_title": "End User License Agreement & Proprietary Rights",



        "license_rights": "Developed by: scar development\nCopyright (c) 2026 scar development. All Rights Reserved.",



        "license_body": (



            "SCAR RAR v1.0 [100% Free Edition]\n\n"



            "PROPRIETARY RIGHTS & COPYRIGHT NOTICE:\n"



            "This software, its source code, encrypted binary payloads, and user interface designs are the exclusive proprietary property of 'scar development'.\n\n"



            "TERMS OF USE:\n"



            "1. Free License: You are granted a 100% free, perpetual, non-exclusive license to use this software for both personal and commercial purposes.\n"



            "2. Anti-Tampering & Protection: You may not decompile, disassemble, reverse engineer, decrypt, modify, or create derivative works from the application binary.\n"



            "3. Integrity: The program files are cryptographically protected to ensure authenticity and safety.\n\n"



            "By clicking 'Next', you agree to these terms."



        ),



        "license_agree": "I accept the license terms and acknowledge scar development rights",



        "dir_prompt": "Setup will install SCAR RAR into the following folder:",



        "btn_browse": "Browse...",



        "opts_title": "Select Additional Tasks:",



        "opt_desktop": "Create a Desktop shortcut",



        "opt_start": "Create a Start Menu shortcut",



        "opt_assoc": "Associate with archive files (.rar, .zip, .7z, .iso, .tar, .gz)",



        "opt_context": "Add SCAR RAR to Windows right-click context menu",



        "btn_next": "Next >",



        "btn_back": "< Back",



        "btn_install": "Install Now",



        "btn_cancel": "Cancel",



        "btn_finish": "Finish",



        "installing_title": "Installing SCAR RAR on your system...",



        "install_step_prep": "Preparing installation directory...",



        "install_step_extract": "Decrypting and deploying secure program files...",



        "install_step_lang": "Configuring language and user preferences...",



        "install_step_shortcuts": "Creating Desktop and Start Menu shortcuts...",



        "install_step_registry": "Registering Windows shell integration and associations...",



        "install_step_done": "Installation completed successfully!",



                "maint_title_update": "SCAR RAR Update Available",
        "maint_badge_update": "Update Available",
        "maint_desc_update": "A previous version of SCAR RAR was detected. An update with the latest performance enhancements and features is available!",
        "maint_title_same": "SCAR RAR is Already Installed",
        "maint_badge_same": "Already Installed",
        "maint_desc_same": "SCAR RAR is already installed on your computer. Please choose an action below:",
        "maint_curr_ver": "Installed Version: {ver}",
        "maint_new_ver": "New Version: {ver}",
        "maint_already_latest": "Latest Version",
        "maint_loc": "Installation Directory: {loc}",
        "btn_update": "Update SCAR RAR Now",
        "btn_update_sub": "Directly upgrade all program files to the latest version while preserving your settings and favorites",
        "btn_repair": "Repair SCAR RAR",
        "btn_repair_sub": "Reinstall and repair all core files, restore shell cascading context menus and shortcuts",
        "btn_uninstall": "Uninstall / Remove SCAR RAR",
        "btn_uninstall_sub": "Completely remove SCAR RAR and all of its components from your computer",
        "update_progress_title": "Updating SCAR RAR to latest version...",
        "repair_progress_title": "Repairing and verifying SCAR RAR installation...",
        "update_done_title": "SCAR RAR Updated Successfully!",
        "update_done_msg": "SCAR RAR has been updated to the latest version. All improvements have been applied while preserving your settings.",
        "repair_done_title": "SCAR RAR Repaired Successfully!",
        "repair_done_msg": "All SCAR RAR components, shell context menus, and shortcuts have been fully restored and verified.",
        "finish_title": "SCAR RAR Setup Completed!",



        "finish_msg": "SCAR RAR has been successfully installed on your computer.\n\nAll files are encrypted and protected by scar development.",



        "opt_launch": "Launch SCAR RAR now",



        "warn_agree": "Please accept the license terms to continue.",



        "warn_dir": "Please specify a valid installation folder."



    },



    "العربية": {



        "title": "مثبت برنامج SCAR RAR - تطوير scar development",



        "header_title": "مساعد تثبيت برنامج SCAR RAR",



        "header_subtitle": "محرك الضغط والأرشفة الفائق والأحدث عالمياً",



        "step_lang": "اختيار لغة واجهة البرنامج",



        "step_license": "حقوق الملكية الفكرية وتراخيص الاستخدام",



        "step_dir": "مجلد التثبيت والمهام الإضافية",



        "step_install": "جارٍ تثبيت وحماية ملفات البرنامج",



        "step_finish": "اكتمل تثبيت البرنامج بنجاح",



        "lang_prompt": "اختر لغة واجهة برنامج SCAR RAR الافتراضية:",



        "lang_desc": "سيتم تطبيق هذه اللغة فوراً على برنامج التثبيت وكذلك على تطبيق SCAR RAR المثبت.",



        "license_title": "حقوق الملكية الفكرية وتراخيص الاستخدام",



        "license_rights": "تطوير وبرمجة: scar development\nحقوق النشر (c) 2026 scar development. جميع الحقوق محفوظة.",



        "license_body": (



            "برنامج SCAR RAR v1.0 [النسخة المجانية الرسمية الكاملة]\n\n"



            "إشعار حقوق الملكية الفكرية:\n"



            "هذا البرنامج وكافة شيفراته البرمجية، وملفاته الثنائية المشفرة، وتصاميم واجهاته ملكية حصرية وخاصة بـ 'scar development'.\n\n"



            "شروط الاستخدام:\n"



            "1. ترخيص مجاني: يُمنح المستخدم ترخيصاً مجانياً 100% غير محدود لاستخدام البرنامج للأغراض الشخصية والتجارية مدى الحياة.\n"



            "2. الحماية ومنع التعديل: يمنع منعاً باتاً تفكيك، أو هندسة عكسية، أو فك تشفير، أو التعديل على أي من ملفات البرنامج الثنائية لحماية الشيفرة من أي عبث خارجي.\n"



            "3. الأمان والموثوقية: ملفات البرنامج مشفرة ومؤمنة ضد أي تلاعب أو تعديل غير مصرح به.\n\n"



            "بالضغط على 'التالي'، فإنك تقر وتوافق على هذه البنود."



        ),



        "license_agree": "أوافق على الشروط وأقر بحقوق ملكية scar development",



        "dir_prompt": "سيقوم معالج التثبيت بتثبيت SCAR RAR في المجلد التالي:",



        "btn_browse": "استعراض...",



        "opts_title": "المهام الإضافية المرغوبة:",



        "opt_desktop": "إنشاء اختصار على سطح المكتب",



        "opt_start": "إنشاء اختصار في قائمة ابدأ",



        "opt_assoc": "ربط صيغ الأرشيف المضغوطة بالبرنامج (.rar, .zip, .7z, .iso)",



        "opt_context": "إضافة SCAR RAR لقائمة زر الفأرة الأيمن في ويندوز",



        "btn_next": "التالي >",



        "btn_back": "< السابق",



        "btn_install": "تثبيت الآن",



        "btn_cancel": "إلغاء",



        "btn_finish": "إنهاء",



        "installing_title": "جارٍ تثبيت وحماية ملفات SCAR RAR...",



        "install_step_prep": "تهيئة مجلد التثبيت والنظام...",



        "install_step_extract": "فك تشفير ونشر ملفات البرنامج الآمنة...",



        "install_step_lang": "ضبط اللغة المختارة والإعدادات الافتراضية...",



        "install_step_shortcuts": "إنشاء اختصارات سطح المكتب وقائمة البرامج...",



        "install_step_registry": "تسجيل امتدادات الملفات وقوائم السياق في ويندوز...",



        "install_step_done": "اكتمل التثبيت بنجاح تام!",



                "maint_title_update": "تحديث جديد متوفر لبرنامج SCAR RAR",
        "maint_badge_update": "تحديث متوفر",
        "maint_desc_update": "تم اكتشاف إصدار مثبت مسبقاً من SCAR RAR على جهازك، ويتوفر الآن تحديث بإصدار أحدث ومميزات متطورة!",
        "maint_title_same": "برنامج SCAR RAR مثبت بالفعل",
        "maint_badge_same": "مثبت مسبقاً",
        "maint_desc_same": "برنامج SCAR RAR مثبت بالفعل على حاسوبك بأحدث إصدار. يرجى اختيار الإجراء المطلوب:",
        "maint_curr_ver": "الإصدار المثبت حالياً: {ver}",
        "maint_new_ver": "الإصدار الأحدث المتوفر: {ver}",
        "maint_already_latest": "أحدث إصدار",
        "maint_loc": "مجلد التثبيت: {loc}",
        "btn_update": "تحديث البرنامج الآن",
        "btn_update_sub": "ترقية كافة الملفات والمحركات مباشرة للإصدار الأحدث مع الحفاظ على إعداداتك ومفضلاتك",
        "btn_repair": "إصلاح البرنامج",
        "btn_repair_sub": "إعادة فحص واستعادة كافة ملفات ومحركات البرنامج وإصلاح قوائم الويندوز والاختصارات",
        "btn_uninstall": "إلغاء التثبيت / حذف البرنامج",
        "btn_uninstall_sub": "إزالة برنامج SCAR RAR وجميع مكوناته نهائياً من جهاز الكمبيوتر",
        "update_progress_title": "جارٍ تحديث SCAR RAR إلى أحدث إصدار...",
        "repair_progress_title": "جارٍ فحص وإصلاح ملفات SCAR RAR...",
        "update_done_title": "تم التحديث بنجاح تام!",
        "update_done_msg": "تم تحديث برنامج SCAR RAR إلى أحدث إصدار بنجاح وتطبيق كافة التحسينات دون فقدان أي من إعداداتك ومفضلاتك.",
        "repair_done_title": "تم إصلاح البرنامج بنجاح!",
        "repair_done_msg": "تم فحص واستعادة كافة ملفات ومحركات البرنامج وإصلاح قوائم الويندوز والاختصارات بنجاح.",
        "finish_title": "تم تثبيت SCAR RAR بنجاح!",



        "finish_msg": "تم تثبيت تطبيق SCAR RAR بنجاح تام على حاسوبك.\n\nكافة ملفات التطبيق مشفرة ومحمية بالكامل لـ scar development.",



        "opt_launch": "تشغيل تطبيق SCAR RAR الآن",



        "warn_agree": "يرجى الموافقة على شروط الترخيص للمتابعة.",



        "warn_dir": "يرجى تحديد مسار تثبيت صالح."



    },



    "Français": {



        "title": "Installation de SCAR RAR - scar development",



        "header_title": "Assistant d'installation SCAR RAR",



        "header_subtitle": "Moteur haute performance de compression et d'archivage",



        "step_lang": "Sélection de la langue",



        "step_license": "Contrat de licence et droits de propriété",



        "step_dir": "Dossier de destination et options",



        "step_install": "Installation de SCAR RAR",



        "step_finish": "Fin de l'installation",



        "lang_prompt": "Choisissez la langue de l'interface pour SCAR RAR:",



        "lang_desc": "Cette langue sera appliquée immédiatement à cet installateur et à votre application.",



        "license_title": "Contrat de licence et droits de propriété",



        "license_rights": "Développé par: scar development\nCopyright (c) 2026 scar development. Tous droits réservés.",



        "license_body": (



            "SCAR RAR v1.0 [Édition 100% Gratuite]\n\n"



            "DROITS DE PROPRIÉTÉ ET COPYRIGHT:\n"



            "Ce logiciel, ses binaires protégés et ses interfaces sont la propriété exclusive de 'scar development'.\n\n"



            "CONDITIONS D'UTILISATION:\n"



            "1. Licence gratuite: Vous disposez d'une licence 100% gratuite et illimitée pour un usage personnel et commercial.\n"



            "2. Protection et anti-altération: La décompilation, le désassemblage et la rétro-ingénierie sont strictement interdits.\n\n"



            "En cliquant sur 'Suivant', vous acceptez ces conditions."



        ),



        "license_agree": "J'accepte les termes et reconnais les droits de scar development",



        "dir_prompt": "L'assistant va installer SCAR RAR dans le dossier suivant:",



        "btn_browse": "Parcourir...",



        "opts_title": "Tâches supplémentaires:",



        "opt_desktop": "Créer un raccourci sur le Bureau",



        "opt_start": "Créer un raccourci dans le menu Démarrer",



        "opt_assoc": "Associer aux formats d'archives (.rar, .zip, .7z, .iso)",



        "opt_context": "Intégrer SCAR RAR au menu contextuel de Windows",



        "btn_next": "Suivant >",



        "btn_back": "< Précédent",



        "btn_install": "Installer",



        "btn_cancel": "Annuler",



        "btn_finish": "Terminer",



        "installing_title": "Installation de SCAR RAR en cours...",



        "install_step_prep": "Préparation du dossier d'installation...",



        "install_step_extract": "Déploiement des fichiers sécurisés et chiffrés...",



        "install_step_lang": "Configuration de la langue et des préférences...",



        "install_step_shortcuts": "Création des raccourcis Bureau et menu Démarrer...",



        "install_step_registry": "Enregistrement des associations de fichiers...",



        "install_step_done": "Installation terminée avec succès!",



                "maint_title_update": "Mise à jour de SCAR RAR disponible",
        "maint_badge_update": "Mise à jour disponible",
        "maint_desc_update": "Une version précédente de SCAR RAR a été détectée. Une version plus récente est disponible!",
        "maint_title_same": "SCAR RAR est déjà installé",
        "maint_badge_same": "Déjà installé",
        "maint_desc_same": "SCAR RAR est déjà installé sur votre ordinateur. Veuillez choisir une action:",
        "maint_curr_ver": "Version installée: {ver}",
        "maint_new_ver": "Nouvelle version: {ver}",
        "maint_already_latest": "Dernière version",
        "maint_loc": "Dossier d'installation: {loc}",
        "btn_update": "Mettre à jour maintenant",
        "btn_update_sub": "Mettre à jour directement vers la dernière version en conservant vos paramètres",
        "btn_repair": "Réparer l'installation",
        "btn_repair_sub": "Réinstaller tous les fichiers et réparer les menus contextuels Windows",
        "btn_uninstall": "Désinstaller SCAR RAR",
        "btn_uninstall_sub": "Supprimer complètement SCAR RAR et tous ses composants",
        "update_progress_title": "Mise à jour de SCAR RAR en cours...",
        "repair_progress_title": "Réparation de SCAR RAR en cours...",
        "update_done_title": "Mise à jour terminée avec succès!",
        "update_done_msg": "SCAR RAR a été mis à jour vers la dernière version.",
        "repair_done_title": "Réparation terminée avec succès!",
        "repair_done_msg": "Tous les composants de SCAR RAR ont été réparés avec succès.",
        "finish_title": "Installation de SCAR RAR terminée!",



        "finish_msg": "SCAR RAR a été installé avec succès sur votre ordinateur.\n\nTous les fichiers sont sécurisés et protégés par scar development.",



        "opt_launch": "Lancer SCAR RAR maintenant",



        "warn_agree": "Veuillez accepter les conditions de licence pour continuer.",



        "warn_dir": "Veuillez spécifier un dossier d'installation valide."



    },



    "Español": {



        "title": "Instalador de SCAR RAR - scar development",



        "header_title": "Asistente de instalación de SCAR RAR",



        "header_subtitle": "Motor de compresión y archivado de alto rendimiento",



        "step_lang": "Selección de idioma",



        "step_license": "Acuerdo de licencia y derechos de propiedad",



        "step_dir": "Carpeta de destino y opciones",



        "step_install": "Instalando SCAR RAR",



        "step_finish": "Instalación completada",



        "lang_prompt": "Seleccione el idioma predeterminado de SCAR RAR:",



        "lang_desc": "Este idioma se aplicará tanto al instalador como a la aplicación instalada.",



        "license_title": "Acuerdo de licencia y derechos de propiedad",



        "license_rights": "Desarrollado por: scar development\nCopyright (c) 2026 scar development. Todos los derechos reservados.",



        "license_body": (



            "SCAR RAR v1.0 [Edición 100% Gratuita]\n\n"



            "DERECHOS DE AUTOR Y PROPIEDAD:\n"



            "Este software y sus binarios cifrados son propiedad exclusiva de 'scar development'.\n\n"



            "TÉRMINOS DE USO:\n"



            "1. Licencia gratuita: Licencia perpetua y 100% gratuita para uso personal y comercial.\n"



            "2. Protección de código: Queda estrictamente prohibida la descompilación o modificación de los archivos binarios.\n\n"



            "Al hacer clic en 'Siguiente', acepta estos términos."



        ),



        "license_agree": "Acepto los términos y reconozco los derechos de scar development",



        "dir_prompt": "El instalador instalará SCAR RAR en la siguiente carpeta:",



        "btn_browse": "Examinar...",



        "opts_title": "Tareas adicionales:",



        "opt_desktop": "Crear un acceso directo en el Escritorio",



        "opt_start": "Crear un acceso directo en el Menú Inicio",



        "opt_assoc": "Asociar con formatos de archivo (.rar, .zip, .7z, .iso)",



        "opt_context": "Integrar SCAR RAR en el menú contextual de Windows",



        "btn_next": "Siguiente >",



        "btn_back": "< Anterior",



        "btn_install": "Instalar",



        "btn_cancel": "Cancelar",



        "btn_finish": "Finalizar",



        "installing_title": "Instalando SCAR RAR en su sistema...",



        "install_step_prep": "Preparando carpeta de instalación...",



        "install_step_extract": "Desplegando archivos cifrados y protegidos...",



        "install_step_lang": "Configurando el idioma y las preferencias...",



        "install_step_shortcuts": "Creando accesos directos en el Escritorio e Inicio...",



        "install_step_registry": "Registrando asociaciones de archivos en Windows...",



        "install_step_done": "¡Instalación completada con éxito!",



                "maint_title_update": "Actualización de SCAR RAR disponible",
        "maint_badge_update": "Actualización disponible",
        "maint_desc_update": "Se detectó una instalación previa de SCAR RAR. ¡Hay una versión más reciente disponible!",
        "maint_title_same": "SCAR RAR ya está instalado",
        "maint_badge_same": "Ya instalado",
        "maint_desc_same": "SCAR RAR ya está instalado en su equipo. Seleccione una acción:",
        "maint_curr_ver": "Versión instalada: {ver}",
        "maint_new_ver": "Nueva versión: {ver}",
        "maint_already_latest": "Última versión",
        "maint_loc": "Ruta de instalación: {loc}",
        "btn_update": "Actualizar ahora",
        "btn_update_sub": "Actualizar directamente a la última versión conservando sus ajustes",
        "btn_repair": "Reparar instalación",
        "btn_repair_sub": "Reinstalar todos los componentes y reparar menús contextuales y accesos directos",
        "btn_uninstall": "Desinstalar SCAR RAR",
        "btn_uninstall_sub": "Eliminar SCAR RAR y todos sus componentes del equipo",
        "update_progress_title": "Actualizando SCAR RAR...",
        "repair_progress_title": "Reparando SCAR RAR...",
        "update_done_title": "¡Actualización completada con éxito!",
        "update_done_msg": "SCAR RAR se ha actualizado a la última versión.",
        "repair_done_title": "¡Reparación completada con éxito!",
        "repair_done_msg": "Todos los componentes de SCAR RAR han sido reparados con éxito.",
        "finish_title": "¡Instalación de SCAR RAR completada!",



        "finish_msg": "SCAR RAR se ha instalado correctamente en su equipo.\n\nTodos los archivos están cifrados y protegidos por scar development.",



        "opt_launch": "Ejecutar SCAR RAR ahora",



        "warn_agree": "Por favor acepte los términos de la licencia para continuar.",



        "warn_dir": "Por favor especifique una carpeta de instalación válida."



    }



}











def create_installer_icon():



    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))



    d = ImageDraw.Draw(im)



    pts = [(32, 2), (60, 16), (60, 48), (32, 62), (4, 48), (4, 16)]



    d.polygon(pts, fill='#0d233a', outline='#38bdf8', width=3)



    d.line([(16, 32), (24, 24)], fill='#38bdf8', width=4)



    d.line([(16, 32), (24, 40)], fill='#38bdf8', width=4)



    d.line([(48, 32), (40, 24)], fill='#38bdf8', width=4)



    d.line([(48, 32), (40, 40)], fill='#38bdf8', width=4)



    d.line([(29, 44), (35, 20)], fill='#ffffff', width=4)



    return im











def create_windows_shortcut(target_exe, shortcut_path, icon_path=None, description="SCAR RAR"):



    """إنشاء اختصار رسمي بنظام Windows بواسطة WScript.Shell"""



    try:



        vbs_script = f'''



Set oWS = WScript.CreateObject("WScript.Shell")



sLinkFile = "{shortcut_path}"



Set oLink = oWS.CreateShortcut(sLinkFile)



oLink.TargetPath = "{target_exe}"



oLink.WorkingDirectory = "{os.path.dirname(target_exe)}"



oLink.Description = "{description}"



'''



        if icon_path and os.path.exists(icon_path):



            vbs_script += f'oLink.IconLocation = "{icon_path},0"\n'



        vbs_script += 'oLink.Save\n'







        vbs_path = os.path.join(os.environ.get("TEMP", "."), "make_shortcut.vbs")



        with open(vbs_path, "w", encoding="ascii", errors="ignore") as f:



            f.write(vbs_script)



        CREATE_NO_WINDOW = 0x08000000
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        try:
            subprocess.run(["wscript", "//nologo", vbs_path], check=True, timeout=5, startupinfo=si, creationflags=CREATE_NO_WINDOW)
        except Exception:
            subprocess.run(["cscript", "//nologo", vbs_path], check=True, timeout=5, startupinfo=si, creationflags=CREATE_NO_WINDOW)



        if os.path.exists(vbs_path):



            os.remove(vbs_path)



        return True



    except Exception:



        return False











def register_file_associations(exe_path, icon_path=None, register_assoc=True, register_context=True):



    """تسجيل ربط امتدادات الأرشيف وقائمة السياق التراكمية في ويندوز (مثل WinRAR تماماً بالصورة 4)"""



    exts = [".rar", ".zip", ".7z", ".iso", ".tar", ".gz", ".bz2", ".xz"]



    try:



        import winreg







        def set_key(root, subkey, values={}, default=""):



            with winreg.CreateKey(root, subkey) as k:



                if default is not None:



                    winreg.SetValue(k, "", winreg.REG_SZ, default)



                for v_name, v_val in values.items():



                    winreg.SetValueEx(k, v_name, 0, winreg.REG_SZ, v_val)







        prog_id = "SCAR_RAR_Archive"



        ico_val = icon_path if (icon_path and os.path.exists(icon_path)) else exe_path







        if register_assoc:



            set_key(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}", default="SCAR RAR Archive")



            set_key(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\DefaultIcon", default=f'"{ico_val}",0')



            set_key(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\shell\\open\\command", default=f'"{exe_path}" "%1"')







            for ext in exts:



                try:



                    set_key(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{ext}", default=prog_id)



                except Exception:



                    pass







        if register_context:



            # 1. قائمة سياق الأرشيفات التراكمية تحت SCAR_RAR_Archive



            casc_key = f"Software\\Classes\\{prog_id}\\shell\\SCARRAR"



            set_key(winreg.HKEY_CURRENT_USER, casc_key, {"MUIVerb": "SCAR RAR", "Icon": ico_val, "SubCommands": ""})



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\01_Open", {"MUIVerb": "Open with SCAR RAR", "Icon": ico_val})



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\01_Open\\command", default=f'"{exe_path}" "%1"')



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\02_Extract", {"MUIVerb": "Extract files...", "Icon": ico_val})



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\02_Extract\\command", default=f'"{exe_path}" -e "%1"')



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\03_ExtractHere", {"MUIVerb": "Extract Here", "Icon": ico_val})



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\03_ExtractHere\\command", default=f'"{exe_path}" -x "%1"')



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\04_ExtractToDir", {"MUIVerb": "Extract to subfolder\\", "Icon": ico_val})



            set_key(winreg.HKEY_CURRENT_USER, f"{casc_key}\\shell\\04_ExtractToDir\\command", default=f'"{exe_path}" -xd "%1"')







            # 2. قائمة سياق الأرشيفات تحت SystemFileAssociations لكل امتداد



            for ext in exts:



                try:



                    sfa_casc = f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\SCARRAR"



                    set_key(winreg.HKEY_CURRENT_USER, sfa_casc, {"MUIVerb": "SCAR RAR", "Icon": ico_val, "SubCommands": ""})



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\01_Open", {"MUIVerb": "Open with SCAR RAR", "Icon": ico_val})



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\01_Open\\command", default=f'"{exe_path}" "%1"')



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\02_Extract", {"MUIVerb": "Extract files...", "Icon": ico_val})



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\02_Extract\\command", default=f'"{exe_path}" -e "%1"')



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\03_ExtractHere", {"MUIVerb": "Extract Here", "Icon": ico_val})



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\03_ExtractHere\\command", default=f'"{exe_path}" -x "%1"')



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\04_ExtractToDir", {"MUIVerb": "Extract to subfolder\\", "Icon": ico_val})



                    set_key(winreg.HKEY_CURRENT_USER, f"{sfa_casc}\\shell\\04_ExtractToDir\\command", default=f'"{exe_path}" -xd "%1"')



                except Exception:



                    pass







            # 3. قائمة إضافة إلى الأرشيف لكافة الملفات العادية (*)



            try:



                file_casc = r"Software\Classes\*\shell\SCARRAR"



                set_key(winreg.HKEY_CURRENT_USER, file_casc, {"MUIVerb": "SCAR RAR", "Icon": ico_val, "SubCommands": ""})



                set_key(winreg.HKEY_CURRENT_USER, f"{file_casc}\\shell\\01_Add", {"MUIVerb": "Add to archive...", "Icon": ico_val})



                set_key(winreg.HKEY_CURRENT_USER, f"{file_casc}\\shell\\01_Add\\command", default=f'"{exe_path}" -a "%1"')



                set_key(winreg.HKEY_CURRENT_USER, f"{file_casc}\\shell\\02_AddRar", {"MUIVerb": "Add to archive (RAR)...", "Icon": ico_val})



                set_key(winreg.HKEY_CURRENT_USER, f"{file_casc}\\shell\\02_AddRar\\command", default=f'"{exe_path}" -a "%1"')



            except Exception:



                pass







            # 4. قائمة إضافة إلى الأرشيف للمجلدات (Directory)



            try:



                dir_casc = r"Software\Classes\Directory\shell\SCARRAR"



                set_key(winreg.HKEY_CURRENT_USER, dir_casc, {"MUIVerb": "SCAR RAR", "Icon": ico_val, "SubCommands": ""})



                set_key(winreg.HKEY_CURRENT_USER, f"{dir_casc}\\shell\\01_Add", {"MUIVerb": "Add to archive...", "Icon": ico_val})



                set_key(winreg.HKEY_CURRENT_USER, f"{dir_casc}\\shell\\01_Add\\command", default=f'"{exe_path}" -a "%1"')



                set_key(winreg.HKEY_CURRENT_USER, f"{dir_casc}\\shell\\02_AddRar", {"MUIVerb": "Add to archive (RAR)...", "Icon": ico_val})



                set_key(winreg.HKEY_CURRENT_USER, f"{dir_casc}\\shell\\02_AddRar\\command", default=f'"{exe_path}" -a "%1"')



            except Exception:



                pass







        # إشعار مستكشف ويندوز فوراً لتحديث الأيقونات والقوائم بدون إعادة تشغيل



        try:



            import ctypes



            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)



        except Exception:



            pass



    except Exception:



        pass







def register_uninstaller_in_windows(install_dir, exe_path, icon_path=None):

    """تسجيل البرنامج رسمياً في قائمة إزالة البرامج في ويندوز وRevo Uninstaller"""

    try:

        import winreg

        import datetime



        uninstall_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SCAR RAR"

        uninstaller_exe = os.path.join(install_dir, "uninstall.exe")

        ico_val = icon_path if (icon_path and os.path.exists(icon_path)) else uninstaller_exe



        total_kb = 0

        try:

            for root, dirs, files in os.walk(install_dir):

                for f in files:

                    total_kb += os.path.getsize(os.path.join(root, f)) // 1024

        except Exception:

            total_kb = 125000



        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, uninstall_key) as k:

            winreg.SetValueEx(k, "DisplayName", 0, winreg.REG_SZ, "SCAR RAR")

            winreg.SetValueEx(k, "DisplayVersion", 0, winreg.REG_SZ, CURRENT_INSTALLER_VERSION)

            winreg.SetValueEx(k, "Publisher", 0, winreg.REG_SZ, "scar development")

            winreg.SetValueEx(k, "DisplayIcon", 0, winreg.REG_SZ, f'"{ico_val}",0')

            winreg.SetValueEx(k, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}"')

            winreg.SetValueEx(k, "QuietUninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}" /SILENT')

            winreg.SetValueEx(k, "InstallLocation", 0, winreg.REG_SZ, install_dir)

            winreg.SetValueEx(k, "InstallDate", 0, winreg.REG_SZ, datetime.datetime.now().strftime("%Y%m%d"))

            winreg.SetValueEx(k, "EstimatedSize", 0, winreg.REG_DWORD, total_kb)

            winreg.SetValueEx(k, "HelpLink", 0, winreg.REG_SZ, "https://discord.com/users/989509070908174406")

            winreg.SetValueEx(k, "URLInfoAbout", 0, winreg.REG_SZ, "https://discord.com/users/989509070908174406")

            winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)

            winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)

            winreg.SetValueEx(k, "Comments", 0, winreg.REG_SZ, "SCAR RAR - High-Speed Archive Engine by scar development")



        try:

            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as k:

                winreg.SetValueEx(k, "DisplayName", 0, winreg.REG_SZ, "SCAR RAR")

                winreg.SetValueEx(k, "DisplayVersion", 0, winreg.REG_SZ, CURRENT_INSTALLER_VERSION)

                winreg.SetValueEx(k, "Publisher", 0, winreg.REG_SZ, "scar development")

                winreg.SetValueEx(k, "DisplayIcon", 0, winreg.REG_SZ, f'"{ico_val}",0')

                winreg.SetValueEx(k, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}"')

                winreg.SetValueEx(k, "QuietUninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}" /SILENT')

                winreg.SetValueEx(k, "InstallLocation", 0, winreg.REG_SZ, install_dir)

                winreg.SetValueEx(k, "InstallDate", 0, winreg.REG_SZ, datetime.datetime.now().strftime("%Y%m%d"))

                winreg.SetValueEx(k, "EstimatedSize", 0, winreg.REG_DWORD, total_kb)

                winreg.SetValueEx(k, "HelpLink", 0, winreg.REG_SZ, "https://discord.com/users/989509070908174406")

                winreg.SetValueEx(k, "URLInfoAbout", 0, winreg.REG_SZ, "https://discord.com/users/989509070908174406")

                winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)

                winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)

                winreg.SetValueEx(k, "Comments", 0, winreg.REG_SZ, "SCAR RAR - High-Speed Archive Engine by scar development")

        except Exception:

            pass

    except Exception:

        pass





class ScarInstallerApp:



    def __init__(self, root: tk.Tk):



        self.root = root



        self.mode = "install"  # "install", "update", or "repair"

        self.installed_info = self.detect_existing_installation()

        # إذا كان البرنامج مثبتاً ولديه لغة مفضلة
        self.current_lang = "العربية"
        if self.installed_info and self.installed_info.get("language"):
            self.current_lang = self.installed_info["language"]

        self.current_step = 0



        self.total_steps = 4







        # إعداد نافذة التثبيت العصرية المظلمة



        self.root.title(self.t("title"))



        self.root.geometry("650x520")



        self.root.resizable(False, False)



        self.root.configure(bg="#0c1017")



        self.center_window(650, 520)







        # تفعيل المظهر المظلم في شريط عنوان ويندوز وإزالة الإطار الأبيض



        try:



            self.root.update_idletasks()



            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())



            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)



            # إطار داكن متناسق



            border_color = ctypes.c_int(0x00221711)



            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border_color), 4)



        except Exception:



            pass







        # تهيئة الأيقونة الرسمية



        self.icon_pil = create_installer_icon()



        self.icon_tk = ImageTk.PhotoImage(self.icon_pil)



        try:



            self.root.iconphoto(False, self.icon_tk)



        except Exception:



            pass







        # مسار التثبيت الافتراضي في مساحة المستخدم النظيفة



        default_base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))



        self.dest_dir_var = tk.StringVar(value=os.path.join(default_base, "Programs", "SCAR RAR"))







        # خيارات التثبيت



        self.opt_desktop_var = tk.BooleanVar(value=True)



        self.opt_start_var = tk.BooleanVar(value=True)



        self.opt_assoc_var = tk.BooleanVar(value=True)



        self.opt_context_var = tk.BooleanVar(value=True)



        self.agree_var = tk.BooleanVar(value=False)



        self.launch_var = tk.BooleanVar(value=True)







        self.setup_styles()



        self._build_ui()

        # تشغيل الفحص السريع الذكي في الخلفية فور فتح المثبت بدون أي تأخير للمستخدم
        self._start_fast_background_scanner()

        self.show_step(0)

        # التحقق من تشغيل المثبت في وضع التحديث التلقائي الصامت
        cmd_args = [a.upper() for a in sys.argv[1:]]
        if "/UPDATE" in cmd_args or "--UPDATE" in cmd_args or "/AUTO" in cmd_args or "-UPDATE" in cmd_args:
            self.root.after(350, self.start_update)







    def _start_fast_background_scanner(self):
        """بدء عملية فحص سريعة وذكية في الخلفية دون أي تعطيل أو إشعار للمستخدم"""
        t = threading.Thread(target=self._run_fast_background_scan, daemon=True)
        t.start()

    def _run_fast_background_scan(self):
        """فحص سريع للخلفية: فحص السجل، الملفات، الإصدار الحقيقي والتحديث التلقائي الصامت"""
        try:
            fresh_info = self.detect_existing_installation()
            if fresh_info:
                # فحص ما إذا كان SCAR RAR قيد التشغيل حالياً
                is_running = False
                try:
                    import subprocess
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    si.wShowWindow = 0
                    out = subprocess.check_output(
                        ["tasklist", "/FI", "IMAGENAME eq SCAR RAR.exe", "/NH"],
                        startupinfo=si,
                        creationflags=0x08000000,
                        stderr=subprocess.DEVNULL
                    ).decode("utf-8", errors="ignore")
                    if "SCAR RAR.exe" in out:
                        is_running = True
                except Exception:
                    pass
                fresh_info["is_running"] = is_running

                # مزامنة السجل الصامتة فورياً إن كان قديماً
                loc = fresh_info.get("location")
                ver = fresh_info.get("version")
                if winreg and ver and loc:
                    for rkey in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                        try:
                            with winreg.OpenKey(rkey, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SCAR RAR", 0, winreg.KEY_SET_VALUE) as k:
                                winreg.SetValueEx(k, "DisplayVersion", 0, winreg.REG_SZ, ver)
                        except Exception:
                            pass

                # إرسال النتائج المحدثة إلى الخيط الرئيسي لتحديث الواجهة بسلاسة
                self.root.after(0, lambda: self._apply_background_scan_results(fresh_info))
        except Exception:
            pass

    def _apply_background_scan_results(self, fresh_info):
        """تطبيق نتائج الفحص الخلفي على الواجهة بسلاسة ودون وميض"""
        prev_update = self.installed_info.get("is_update") if self.installed_info else None
        self.installed_info = fresh_info
        if self.current_step == "maintenance":
            # تحديث الواجهة إذا كان هناك تغيير في حالة التحديث أو الإصدار
            new_update = fresh_info.get("is_update")
            if prev_update != new_update or fresh_info.get("version") != getattr(self, "_last_rendered_ver", None):
                self._render_step_maintenance()

    def detect_existing_installation(self):
        """التحقق بدقة فائقة مما إذا كان البرنامج مثبتاً وقراءة الإصدار الحقيقي من الملفات والسجل"""
        info = {}

        # 1. فحص المجلد الافتراضي في LocalAppData ومجلدات البرامج
        default_base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        candidates = [
            os.path.join(default_base, "Programs", "SCAR RAR"),
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "SCAR RAR"),
            os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "SCAR RAR")
        ]

        # 2. فحص سجل ويندوز (Registry) للحصول على المسار المسجل والإصدار
        reg_loc = None
        reg_ver = None
        if winreg:
            for root_key in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(root_key, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SCAR RAR", 0, winreg.KEY_READ) as k:
                        try: reg_loc, _ = winreg.QueryValueEx(k, "InstallLocation")
                        except Exception: pass
                        try: reg_ver, _ = winreg.QueryValueEx(k, "DisplayVersion")
                        except Exception: pass
                        if reg_loc:
                            break
                except Exception:
                    pass

        # تحديد المسار الفعلي المثبت
        found_loc = None
        if reg_loc and os.path.isdir(reg_loc) and os.path.exists(os.path.join(reg_loc, "SCAR RAR.exe")):
            found_loc = reg_loc
        else:
            for c in candidates:
                if c and os.path.isdir(c) and os.path.exists(os.path.join(c, "SCAR RAR.exe")):
                    found_loc = c
                    break

        if found_loc:
            info["location"] = os.path.abspath(found_loc)

            # تحديد الإصدار الفعلي: الأولوية المطلقة لملف version.txt الموجود داخل مجلد التثبيت
            installed_ver = None
            v_file = os.path.join(found_loc, "version.txt")
            if os.path.exists(v_file):
                try:
                    v_str = open(v_file, "r", encoding="utf-8").read().strip()
                    if v_str:
                        installed_ver = v_str
                except Exception:
                    pass

            # إذا لم يوجد version.txt، نأخذ الإصدار من السجل
            if not installed_ver and reg_ver:
                installed_ver = str(reg_ver).strip()

            # إذا لم يتوفر أي منهما، نعتبره 1.0.0
            if not installed_ver:
                installed_ver = "1.0.0"

            info["version"] = installed_ver

            # قراءة لغة المستخدم المفضلة من ملف الإعدادات
            s_file = os.path.join(found_loc, "scarrar_settings.json")
            if os.path.exists(s_file):
                try:
                    import json
                    with open(s_file, "r", encoding="utf-8") as sf:
                        s_data = json.load(sf)
                        if "language" in s_data:
                            info["language"] = s_data["language"]
                except Exception:
                    pass

            def parse_ver(v_str):
                try:
                    clean = str(v_str).lower().replace("v", "").strip()
                    parts = [int(p) for p in clean.split(".") if p.isdigit()]
                    return tuple(parts) if parts else (1, 0, 0)
                except Exception:
                    return (1, 0, 0)

            curr_v = parse_ver(CURRENT_INSTALLER_VERSION)
            inst_v = parse_ver(installed_ver)

            # التحديث يكون متاحاً فقط إذا كان إصدار المثبت أعلى رقمياً من الإصدار المثبت
            is_newer = (curr_v > inst_v)
            info["is_update"] = is_newer
            info["is_latest"] = (curr_v <= inst_v)
            return info

        return None

    def setup_styles(self):



        """تطبيق سمة clam وأشرطة التمرير والتقدم المظلمة المطابقة لبرنامج SCAR RAR بدقة"""



        style = ttk.Style()



        try:



            style.theme_use('clam')



        except Exception:



            pass







        # شريط التمرير المظلم الخالي من الشريط واللون الأبيض



        style.configure(



            "Scar.Vertical.TScrollbar",



            background="#1e293b",



            troughcolor="#0a0f1d",



            bordercolor="#0c1017",



            lightcolor="#1e293b",



            darkcolor="#0c1017",



            arrowcolor="#64748b",



            arrowsize=10,



            width=12



        )



        style.map(



            "Scar.Vertical.TScrollbar",



            background=[("active", "#38bdf8"), ("pressed", "#0066cc")],



            arrowcolor=[("active", "#ffffff"), ("pressed", "#ffffff")]



        )







        # شريط تقدم العمليات المظلم



        style.configure(



            "Scar.Horizontal.TProgressbar",



            background="#0066cc",



            troughcolor="#111722",



            bordercolor="#1e293b",



            lightcolor="#0066cc",



            darkcolor="#0066cc",



            thickness=14



        )







    def center_window(self, w, h):



        sw = self.root.winfo_screenwidth()



        sh = self.root.winfo_screenheight()



        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")







    def t(self, key: str, **kwargs) -> str:

        d = INSTALLER_I18N.get(self.current_lang, INSTALLER_I18N["English"])

        val = d.get(key, INSTALLER_I18N["English"].get(key, key))
        if kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                pass
        return val







    def _build_ui(self):



        # 1. شريط العنوان والبانر العلوي



        self.header_frame = tk.Frame(self.root, bg="#111722", height=68)



        self.header_frame.pack(fill="x", side="top")



        self.header_frame.pack_propagate(False)







        self.logo_lbl = tk.Label(self.header_frame, image=self.icon_tk, bg="#111722")



        self.logo_lbl.pack(side="left", padx=16, pady=8)







        info_box = tk.Frame(self.header_frame, bg="#111722")



        info_box.pack(side="left", fill="y", pady=12)







        self.hdr_title_lbl = tk.Label(info_box, text=self.t("header_title"),



                                      bg="#111722", fg="#38bdf8", font=("Segoe UI", 12, "bold"))



        self.hdr_title_lbl.pack(anchor="w")







        self.hdr_sub_lbl = tk.Label(info_box, text=self.t("header_subtitle"),



                                    bg="#111722", fg="#94a3b8", font=("Segoe UI", 9))



        self.hdr_sub_lbl.pack(anchor="w")







        # خط فاصل علوي



        tk.Frame(self.root, bg="#1e293b", height=1).pack(fill="x", side="top")







        # 2. شريط الأزرار السفلي (يتم حزمه أولاً في الأسفل لضمان بقائه ظاهراً دائماً)



        self.btn_bar = tk.Frame(self.root, bg="#111722", height=54)



        self.btn_bar.pack(fill="x", side="bottom")



        self.btn_bar.pack_propagate(False)







        # خط فاصل سفلي فوق شريط الأزرار



        tk.Frame(self.root, bg="#1e293b", height=1).pack(fill="x", side="bottom")







        self.rights_lbl = tk.Label(self.btn_bar, text="scar development © 2026",



                                   bg="#111722", fg="#475569", font=("Segoe UI", 8))



        self.rights_lbl.pack(side="left", padx=16, pady=16)







        # أزرار التنقل (Next, Back, Cancel)



        self.btn_cancel = tk.Button(self.btn_bar, text=self.t("btn_cancel"),



                                    bg="#1e293b", fg="#94a3b8", activebackground="#334155", activeforeground="#ffffff",



                                    font=("Segoe UI", 9), bd=0, relief="flat", padx=14, pady=4,



                                    command=self.root.destroy)



        self.btn_cancel.pack(side="right", padx=(6, 16), pady=10)







        self.btn_next = tk.Button(self.btn_bar, text=self.t("btn_next"),



                                  bg="#0066cc", fg="#ffffff", activebackground="#0052a3", activeforeground="#ffffff",



                                  font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=18, pady=4,



                                  command=self.on_next)



        self.btn_next.pack(side="right", padx=6, pady=10)







        self.btn_back = tk.Button(self.btn_bar, text=self.t("btn_back"),



                                  bg="#1e293b", fg="#94a3b8", activebackground="#334155", activeforeground="#ffffff",



                                  font=("Segoe UI", 9), bd=0, relief="flat", padx=14, pady=4,



                                  command=self.on_back)



        self.btn_back.pack(side="right", padx=6, pady=10)







        # 3. منطقة المحتوى التفاعلية الوسطية (تملأ المساحة بالكامل بين البانر والفوتر)



        self.content_frame = tk.Frame(self.root, bg="#0c1017", padx=24, pady=12)



        self.content_frame.pack(fill="both", expand=True)







    def change_language(self, new_lang: str):



        self.current_lang = new_lang



        self.root.title(self.t("title"))



        self.hdr_title_lbl.config(text=self.t("header_title"))



        self.hdr_sub_lbl.config(text=self.t("header_subtitle"))



        self.btn_cancel.config(text=self.t("btn_cancel"))



        self.btn_back.config(text=self.t("btn_back"))



        self.show_step(self.current_step)







    def clear_content(self):



        for widget in self.content_frame.winfo_children():



            widget.destroy()







    def show_step(self, step_idx: int):



        self.current_step = step_idx



        self.clear_content()







        # ضبط حالة الأزرار السفلية بدقة لكل خطوة



        if step_idx == "maintenance":

            self._render_step_maintenance()

        elif step_idx == 0:

            self._render_step_language()



        elif step_idx == 1:



            self._render_step_license()



        elif step_idx == 2:



            self._render_step_directory()



        elif step_idx == 3:



            self._render_step_installing()



        elif step_idx == 4:



            self._render_step_finished()







    # --------------------------------------------------------------------------



    # الخطوة 1: اختيار لغة التثبيت والبرنامج (Language Selection)



    # --------------------------------------------------------------------------



    def _render_step_maintenance(self):
        """عرض شاشة إدارة التثبيت الذكية: خيار التحديث المباشر إذا توفر إصدار أحدث، أو خياري الإصلاح والحذف"""
        self.btn_next.pack_forget()
        self.btn_back.pack(side="right", padx=6, pady=10)
        self.btn_cancel.pack(side="right", padx=(6, 16), pady=10)
        self.btn_cancel.config(text=self.t("btn_cancel"), state="normal")
        self.btn_back.config(text=self.t("btn_back"), state="normal", command=self.on_back)

        info = self.installed_info or {}
        is_update = info.get("is_update", False)
        installed_ver = info.get("version", "1.0.0")
        install_loc = info.get("location", self.dest_dir_var.get())
        self._last_rendered_ver = installed_ver

        hdr_frame = tk.Frame(self.content_frame, bg="#0c1017")
        hdr_frame.pack(fill="x", pady=(0, 6))

        if is_update:
            badge_bg = "#0369a1"
            badge_fg = "#e0f2fe"
            badge_text = f"🚀  {self.t('maint_badge_update')}"
            title_text = self.t("maint_title_update")
            title_color = "#38bdf8"
            desc_text = self.t("maint_desc_update")
        else:
            badge_bg = "#065f46"
            badge_fg = "#d1fae5"
            badge_text = f"ℹ️  {self.t('maint_badge_same')}"
            title_text = self.t("maint_title_same")
            title_color = "#10b981"
            desc_text = self.t("maint_desc_same")

        badge_lbl = tk.Label(hdr_frame, text=f"  {badge_text}  ", bg=badge_bg, fg=badge_fg,
                             font=("Segoe UI", 9, "bold"))
        badge_lbl.pack(anchor="center", pady=(0, 4))

        tk.Label(hdr_frame, text=title_text, bg="#0c1017", fg=title_color,
                 font=("Segoe UI", 13, "bold"), justify="center").pack(anchor="center", pady=(0, 2))

        tk.Label(hdr_frame, text=desc_text, bg="#0c1017", fg="#94a3b8",
                 font=("Segoe UI", 9), justify="center", wraplength=560).pack(anchor="center", pady=(0, 4))

        # بطاقة تفاصيل الإصدار والمسار
        info_card = tk.Frame(self.content_frame, bg="#111827", highlightbackground="#1e293b", highlightthickness=1)
        info_card.pack(fill="x", padx=10, pady=(0, 10))

        if is_update:
            ver_line = f"✔  {self.t('maint_curr_ver', ver=installed_ver)}    ➔    🚀  {self.t('maint_new_ver', ver=CURRENT_INSTALLER_VERSION)}"
        else:
            ver_line = f"✔  {self.t('maint_curr_ver', ver=installed_ver)}  ({self.t('maint_already_latest')})"

        tk.Label(info_card, text=ver_line, bg="#111827", fg="#38bdf8" if is_update else "#10b981",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(6, 2))

        loc_line = f"📁  {self.t('maint_loc', loc=install_loc)}"
        tk.Label(info_card, text=loc_line, bg="#111827", fg="#64748b",
                 font=("Segoe UI", 8), anchor="w").pack(anchor="w", padx=12, pady=(0, 6))

        # حاوية البطاقات التفاعلية للأزرار
        actions_frame = tk.Frame(self.content_frame, bg="#0c1017")
        actions_frame.pack(fill="both", expand=True, padx=10)

        # 1. بطاقة الخيار الأساسي (تحديث أو إصلاح)
        c1_border = "#0284c7" if is_update else "#059669"
        c1_hover = "#1e293b"
        card1 = tk.Frame(actions_frame, bg="#131b28", highlightbackground=c1_border, highlightthickness=1, cursor="hand2")
        card1.pack(fill="x", pady=(0, 8))

        c1_icon = "🚀" if is_update else "🔧"
        c1_title = self.t("btn_update") if is_update else self.t("btn_repair")
        c1_sub = self.t("btn_update_sub") if is_update else self.t("btn_repair_sub")
        c1_cmd = self.start_update if is_update else self.start_repair

        lbl_c1_icon = tk.Label(card1, text=c1_icon, bg="#131b28", fg="#38bdf8" if is_update else "#10b981", font=("Segoe UI", 20))
        lbl_c1_icon.pack(side="left" if self.current_lang != "العربية" else "right", padx=16, pady=8)

        txt_box1 = tk.Frame(card1, bg="#131b28")
        txt_box1.pack(side="left" if self.current_lang != "العربية" else "right", fill="both", expand=True, pady=8, padx=6)

        lbl_c1_title = tk.Label(txt_box1, text=c1_title, bg="#131b28", fg="#ffffff", font=("Segoe UI", 11, "bold"), anchor="w" if self.current_lang != "العربية" else "e")
        lbl_c1_title.pack(fill="x")

        lbl_c1_sub = tk.Label(txt_box1, text=c1_sub, bg="#131b28", fg="#94a3b8", font=("Segoe UI", 8), anchor="w" if self.current_lang != "العربية" else "e", wraplength=440, justify="left" if self.current_lang != "العربية" else "right")
        lbl_c1_sub.pack(fill="x", pady=(2, 0))

        def _on_enter1(e):
            for w in (card1, lbl_c1_icon, txt_box1, lbl_c1_title, lbl_c1_sub): w.configure(bg=c1_hover)
        def _on_leave1(e):
            for w in (card1, lbl_c1_icon, txt_box1, lbl_c1_title, lbl_c1_sub): w.configure(bg="#131b28")

        for w in (card1, lbl_c1_icon, txt_box1, lbl_c1_title, lbl_c1_sub):
            w.bind("<Enter>", _on_enter1)
            w.bind("<Leave>", _on_leave1)
            w.bind("<Button-1>", lambda e, cmd=c1_cmd: cmd())

        # 2. بطاقة خيار إلغاء التثبيت / الحذف
        card2_hover = "#271419"
        card2 = tk.Frame(actions_frame, bg="#181116", highlightbackground="#7f1d1d", highlightthickness=1, cursor="hand2")
        card2.pack(fill="x")

        lbl_c2_icon = tk.Label(card2, text="🗑️", bg="#181116", fg="#ef4444", font=("Segoe UI", 20))
        lbl_c2_icon.pack(side="left" if self.current_lang != "العربية" else "right", padx=16, pady=8)

        txt_box2 = tk.Frame(card2, bg="#181116")
        txt_box2.pack(side="left" if self.current_lang != "العربية" else "right", fill="both", expand=True, pady=8, padx=6)

        lbl_c2_title = tk.Label(txt_box2, text=self.t("btn_uninstall"), bg="#181116", fg="#ffffff", font=("Segoe UI", 11, "bold"), anchor="w" if self.current_lang != "العربية" else "e")
        lbl_c2_title.pack(fill="x")

        lbl_c2_sub = tk.Label(txt_box2, text=self.t("btn_uninstall_sub"), bg="#181116", fg="#94a3b8", font=("Segoe UI", 8), anchor="w" if self.current_lang != "العربية" else "e", wraplength=440, justify="left" if self.current_lang != "العربية" else "right")
        lbl_c2_sub.pack(fill="x", pady=(2, 0))

        def _on_enter2(e):
            for w in (card2, lbl_c2_icon, txt_box2, lbl_c2_title, lbl_c2_sub): w.configure(bg=card2_hover)
        def _on_leave2(e):
            for w in (card2, lbl_c2_icon, txt_box2, lbl_c2_title, lbl_c2_sub): w.configure(bg="#181116")

        for w in (card2, lbl_c2_icon, txt_box2, lbl_c2_title, lbl_c2_sub):
            w.bind("<Enter>", _on_enter2)
            w.bind("<Leave>", _on_leave2)
            w.bind("<Button-1>", lambda e: self.start_uninstall())

    def start_update(self):
        self.mode = "update"
        if self.installed_info and self.installed_info.get("location"):
            self.dest_dir_var.set(self.installed_info["location"])
        self.show_step(3)

    def start_repair(self):
        self.mode = "repair"
        if self.installed_info and self.installed_info.get("location"):
            self.dest_dir_var.set(self.installed_info["location"])
        self.show_step(3)

    def start_uninstall(self):
        loc = self.installed_info.get("location") if self.installed_info else None
        if not loc:
            loc = self.dest_dir_var.get()
        uninst_exe = os.path.join(loc, "uninstall.exe")
        if os.path.exists(uninst_exe):
            subprocess.Popen([uninst_exe])
            self.root.destroy()
        else:
            base_src = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            local_uninst = os.path.join(base_src, "uninstall.exe")
            if os.path.exists(local_uninst):
                subprocess.Popen([local_uninst, f"--target={loc}"])
                self.root.destroy()
            else:
                messagebox.showerror("SCAR RAR", "Could not locate uninstall.exe")

    def _render_step_language(self):



        self.btn_back.pack_forget()



        self.btn_cancel.pack(side="right", padx=(6, 16), pady=10)



        self.btn_next.pack(side="right", padx=6, pady=10)



        self.btn_next.config(text=self.t("btn_next"), state="normal", command=self.on_next)







        # العناوين الرئيسية في المنتصف



        tk.Label(self.content_frame, text=f"🌐 {self.t('step_lang')}",



                 bg="#0c1017", fg="#38bdf8", font=("Segoe UI", 13, "bold")).pack(anchor="center", pady=(0, 4))







        tk.Label(self.content_frame, text=self.t("lang_prompt"),



                 bg="#0c1017", fg="#ffffff", font=("Segoe UI", 10), justify="center").pack(anchor="center", pady=(0, 2))







        tk.Label(self.content_frame, text=self.t("lang_desc"),



                 bg="#0c1017", fg="#94a3b8", font=("Segoe UI", 9), justify="center").pack(anchor="center", pady=(0, 14))







        langs = [



            ("العربية", "العربية - Arabic", "🇸🇦"),



            ("English", "English - US / Global", "🇬🇧"),



            ("Français", "Français - French", "🇫🇷"),



            ("Español", "Español - Spanish", "🇪🇸")



        ]







        card_container = tk.Frame(self.content_frame, bg="#0c1017")



        card_container.pack(fill="x", padx=30, pady=4)







        self.lang_radio_var = tk.StringVar(value=self.current_lang)







        for l_id, l_name, flag in langs:



            f = tk.Frame(card_container, bg="#111722", bd=1, highlightbackground="#1e293b", highlightthickness=1)



            f.pack(fill="x", pady=4)







            def _select_lang(val=l_id):



                self.lang_radio_var.set(val)



                self.change_language(val)







            r = tk.Radiobutton(f, text=f"{flag}  {l_name}", variable=self.lang_radio_var, value=l_id,



                               bg="#111722", fg="#e2e8f0", selectcolor="#16202e",



                               activebackground="#111722", activeforeground="#38bdf8",



                               font=("Segoe UI", 10, "bold" if self.current_lang == l_id else "normal"),



                               command=lambda val=l_id: _select_lang(val))



            r.pack(side="left", padx=14, pady=8)







    # --------------------------------------------------------------------------



    # الخطوة 2: حقوق الملكية الفكرية وشروط الترخيص (License & Rights)



    # --------------------------------------------------------------------------



    def _render_step_license(self):



        # إظهار أزرار Next و Back و Cancel بوضوح في شريط الأزرار



        self.btn_cancel.pack(side="right", padx=(6, 16), pady=10)



        self.btn_next.pack(side="right", padx=6, pady=10)



        self.btn_back.pack(side="right", padx=6, pady=10)



        self.btn_next.config(text=self.t("btn_next"), state="normal", command=self.on_next)



        self.btn_back.config(state="normal", command=self.on_back)







        # 1. العناوين الرئيسية في المنتصف (فالنص) كما طلب المستخدم



        tk.Label(self.content_frame, text=f"📜 {self.t('license_title')}",



                 bg="#0c1017", fg="#38bdf8", font=("Segoe UI", 12, "bold"), justify="center").pack(anchor="center", pady=(0, 3))







        tk.Label(self.content_frame, text=self.t("license_rights"),



                 bg="#0c1017", fg="#10b981", font=("Segoe UI", 9, "bold"), justify="center").pack(anchor="center", pady=(0, 6))







        # 2. إطار صندوق النص المظلم المطابق للبرنامج (إلغاء أي إطارات بيضاء)



        t_frame = tk.Frame(self.content_frame, bg="#111722", bd=1, highlightbackground="#1e293b", highlightthickness=1)



        t_frame.pack(fill="both", expand=True, pady=(0, 6))







        txt = tk.Text(t_frame, bg="#0e131d", fg="#cbd5e1", font=("Segoe UI", 9),



                      bd=0, relief="flat", padx=10, pady=8, wrap="word", height=8,



                      highlightthickness=0)



        txt.pack(side="left", fill="both", expand=True)







        # 3. شريط التمرير المظلم المطابق للتطبيق (إلغاء الشريط الأبيض نهائياً)



        vsb = ttk.Scrollbar(t_frame, orient="vertical", command=txt.yview, style="Scar.Vertical.TScrollbar")



        txt.configure(yscrollcommand=vsb.set)



        vsb.pack(side="right", fill="y")







        txt.insert("1.0", self.t("license_body"))



        txt.configure(state="disabled")







        # 4. مربع الموافقة على الشروط متمركز أيضاً



        c = tk.Checkbutton(self.content_frame, text=self.t("license_agree"),



                           variable=self.agree_var, bg="#0c1017", fg="#ffffff",



                           selectcolor="#16202e", activebackground="#0c1017", activeforeground="#38bdf8",



                           font=("Segoe UI", 9, "bold"))



        c.pack(anchor="center", pady=4)







    # --------------------------------------------------------------------------



    # الخطوة 3: مجلد التثبيت والمهام الإضافية (Destination & Options)



    # --------------------------------------------------------------------------



    def _render_step_directory(self):



        self.btn_cancel.pack(side="right", padx=(6, 16), pady=10)



        self.btn_next.pack(side="right", padx=6, pady=10)



        self.btn_back.pack(side="right", padx=6, pady=10)



        self.btn_next.config(text=self.t("btn_install"), state="normal", command=self.on_next)



        self.btn_back.config(state="normal", command=self.on_back)







        # العناوين الرئيسية في المنتصف



        tk.Label(self.content_frame, text=f"📁 {self.t('step_dir')}",



                 bg="#0c1017", fg="#38bdf8", font=("Segoe UI", 12, "bold"), justify="center").pack(anchor="center", pady=(0, 4))







        tk.Label(self.content_frame, text=self.t("dir_prompt"),



                 bg="#0c1017", fg="#e2e8f0", font=("Segoe UI", 9), justify="center").pack(anchor="center", pady=(0, 6))







        p_box = tk.Frame(self.content_frame, bg="#0c1017")



        p_box.pack(fill="x", padx=20, pady=(0, 12))







        e = tk.Entry(p_box, textvariable=self.dest_dir_var, bg="#16202e", fg="#ffffff",



                     insertbackground="#ffffff", bd=0, relief="flat", font=("Segoe UI", 9),



                     highlightthickness=1, highlightbackground="#1e293b")



        e.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 6))







        tk.Button(p_box, text=self.t("btn_browse"), bg="#1e293b", fg="#cbd5e1",



                  activebackground="#334155", activeforeground="#ffffff",



                  font=("Segoe UI", 8), bd=0, relief="flat", padx=10,



                  command=self._browse_dir).pack(side="right")







        opts_box = tk.Frame(self.content_frame, bg="#111722", bd=1, highlightbackground="#1e293b", highlightthickness=1, padx=14, pady=10)



        opts_box.pack(fill="x", padx=20, pady=(4, 0))







        tk.Label(opts_box, text=self.t("opts_title"),



                 bg="#111722", fg="#38bdf8", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))







        opts = [



            (self.t("opt_desktop"), self.opt_desktop_var),



            (self.t("opt_start"), self.opt_start_var),



            (self.t("opt_assoc"), self.opt_assoc_var),



            (self.t("opt_context"), self.opt_context_var),



        ]



        for opt_text, opt_var in opts:



            cb = tk.Checkbutton(opts_box, text=opt_text, variable=opt_var,



                                bg="#111722", fg="#cbd5e1", selectcolor="#16202e",



                                activebackground="#111722", activeforeground="#ffffff",



                                font=("Segoe UI", 9))



            cb.pack(anchor="w", pady=2)







    def _browse_dir(self):



        d = filedialog.askdirectory(parent=self.root, title=self.t("dir_prompt"),



                                    initialdir=self.dest_dir_var.get())



        if d:



            self.dest_dir_var.set(os.path.join(d, "SCAR RAR"))







    # --------------------------------------------------------------------------



    # الخطوة 4: عملية التثبيت وتفكيك وتشفير الحزمة (Installing)



    # --------------------------------------------------------------------------



    def _render_step_installing(self):



        self.btn_back.pack_forget()



        self.btn_next.pack_forget()



        self.btn_cancel.config(state="disabled")







        step_t = self.t('installing_title')
        if getattr(self, "mode", "install") == "update":
            step_t = self.t("update_progress_title")
        elif getattr(self, "mode", "install") == "repair":
            step_t = self.t("repair_progress_title")
        tk.Label(self.content_frame, text=f"⚙  {step_t}",



                 bg="#0c1017", fg="#38bdf8", font=("Segoe UI", 12, "bold"), justify="center").pack(anchor="center", pady=(0, 16))







        self.progress_bar = ttk.Progressbar(self.content_frame, orient="horizontal", mode="determinate",



                                            length=540, style="Scar.Horizontal.TProgressbar")



        self.progress_bar.pack(fill="x", padx=20, pady=(10, 8))







        self.status_lbl = tk.Label(self.content_frame, text=self.t("install_step_prep"),



                                   bg="#0c1017", fg="#ffffff", font=("Segoe UI", 9, "bold"), anchor="center")



        self.status_lbl.pack(fill="x", pady=4)







        self.detail_lbl = tk.Label(self.content_frame, text="",



                                   bg="#0c1017", fg="#64748b", font=("Consolas", 8), anchor="center")



        self.detail_lbl.pack(fill="x")







        # تشغيل التثبيت في مسار خلفي منفصل



        threading.Thread(target=self._run_installation, daemon=True).start()







    def _run_installation(self):



        dest = self.dest_dir_var.get()



        time.sleep(0.3)







        # 1. إعداد المجلد



        self._update_progress(10, self.t("install_step_prep"), dest)



        os.makedirs(dest, exist_ok=True)
        try:
            CREATE_NO_WINDOW = 0x08000000
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            subprocess.run(["taskkill", "/f", "/im", "SCAR RAR.exe"], capture_output=True, timeout=2, startupinfo=si, creationflags=CREATE_NO_WINDOW)
            time.sleep(0.3)
        except Exception:
            pass



        time.sleep(0.4)







        # 2. فك تشفير وتثبيت حزمة البرنامج المحمية لـ scar development



        self._update_progress(30, self.t("install_step_extract"), "Decrypting and deploying secure SCAR RAR binaries...")



        base_src = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))



        enc_payload = os.path.join(base_src, "scar_payload.enc")



        payload_extracted = False







        if os.path.exists(enc_payload):



            try:



                import io, zipfile, hashlib



                with open(enc_payload, "rb") as fin:



                    expected_magic = b"SCAR_RAR_ENCRYPTED_PAYLOAD_V1\x00"



                    magic = fin.read(len(expected_magic))



                    stored_checksum = fin.read(32)



                    enc_data = bytearray(fin.read())







                key_mat = b"scar-development-scarrar-secure-protection-key-2026-v1.0"



                derived_k = hashlib.sha256(key_mat).digest()



                k_len = len(derived_k)







                for i in range(len(enc_data)):



                    enc_data[i] ^= derived_k[i % k_len]







                zf = zipfile.ZipFile(io.BytesIO(enc_data))



                total_f = len(zf.namelist())



                for idx, member in enumerate(zf.namelist()):



                    if getattr(self, "mode", "install") == "update" and member in ("scarrar_favorites.json", "scarrar_settings.json") and os.path.exists(os.path.join(dest, member)):
                        continue
                    zf.extract(member, dest)



                    if idx % 10 == 0:



                        pct = 30 + int(25 * (idx / max(1, total_f)))



                        self._update_progress(pct, self.t("install_step_extract"), f"Extracting {member}...")



                payload_extracted = True



            except Exception as e:



                pass







        if not payload_extracted:



            # فحص وجود مجلد dist أو الملفات المجمعة



            compiled_dist = os.path.join(base_src, "dist", "SCAR RAR")



            if not os.path.exists(compiled_dist):



                compiled_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "SCAR RAR")







            if os.path.exists(compiled_dist):



                for item in os.listdir(compiled_dist):



                    s = os.path.join(compiled_dist, item)



                    d = os.path.join(dest, item)



                    if os.path.isdir(s):



                        if os.path.exists(d): shutil.rmtree(d)



                        shutil.copytree(s, d)



                    else:



                        shutil.copy2(s, d)



            else:



                payload_files = [



                    "SCAR RAR.exe",



                    "Rar.exe",



                    "UnRAR.exe",



                    "scarrar_icon.ico",



                    "scarrar_favorites.json",



                    "scarrar.py",



                    "version_info.txt"



                ]



                for f in payload_files:



                    src_f = os.path.join(base_src, f)



                    if not os.path.exists(src_f):



                        src_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)



                    if os.path.exists(src_f):



                        shutil.copy2(src_f, os.path.join(dest, f))







        time.sleep(0.5)







        # 3. ضبط وتخصيص اللغة المختارة في الإعدادات فوراً



        self._update_progress(60, self.t("install_step_lang"), f"Language: {self.current_lang}")



        settings_path = os.path.join(dest, "scarrar_settings.json")



        settings_data = {



            "default_format": ".rar",



            "default_extract_dir": "",



            "play_sound": True,



            "low_priority": False,



            "confirm_overwrite": True,



            "auto_close_dialog": False,



            "compression_method": "Normal",



            "dict_size": "32 MB",



            "rar_version": "RAR5",



            "verify_crc": False,
            "security_protection": False,
            "attr_security": False,



            "theme": "Dark Obsidian",



            "language": self.current_lang,



            "viewer_font_size": 10,



            "wrap_viewer_text": True,



            "associations": [".rar", ".zip", ".7z", ".iso", ".tar", ".gz", ".bz2", ".xz"],



            "context_menu": self.opt_context_var.get()



        }



        with open(settings_path, "w", encoding="utf-8") as f:



            json.dump(settings_data, f, indent=4, ensure_ascii=False)







        # أيقونة التثبيت



        ico_dest = os.path.join(dest, "scarrar_icon.ico")



        if not os.path.exists(ico_dest):



            self.icon_pil.save(ico_dest, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)])







        time.sleep(0.4)







        # 4. إنشاء الاختصارات الرسمية في سطح المكتب وقائمة ابدأ



        try:
            with open(os.path.join(dest, "version.txt"), "w", encoding="utf-8") as vf:
                vf.write(CURRENT_INSTALLER_VERSION)
        except Exception:
            pass
        self._update_progress(80, self.t("install_step_shortcuts"), "Creating shortcuts...")



        main_exe = os.path.join(dest, "SCAR RAR.exe")



        if not os.path.exists(main_exe):



            main_exe = os.path.join(dest, "scarrar.py")







        # اختصار سطح المكتب



        if self.opt_desktop_var.get():



            desktop_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")



            if not os.path.exists(desktop_dir):



                desktop_dir = os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Bureau")



            if os.path.exists(desktop_dir):



                shortcut_file = os.path.join(desktop_dir, "SCAR RAR.lnk")



                create_windows_shortcut(main_exe, shortcut_file, ico_dest, "SCAR RAR - scar development")







        # اختصار قائمة ابدأ



        if self.opt_start_var.get():



            appdata = os.environ.get("APPDATA", "")



            if appdata:



                start_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "SCAR RAR")



                os.makedirs(start_dir, exist_ok=True)



                create_windows_shortcut(main_exe, os.path.join(start_dir, "SCAR RAR.lnk"), ico_dest, "SCAR RAR")

                uninst_exe = os.path.join(dest, "uninstall.exe")

                if os.path.exists(uninst_exe):

                    create_windows_shortcut(uninst_exe, os.path.join(start_dir, "Uninstall SCAR RAR.lnk"), ico_dest, "Uninstall SCAR RAR")







        time.sleep(0.4)







        # 5. تسجيل امتدادات الملفات وقوائم السياق في ويندوز



        if self.opt_assoc_var.get() or self.opt_context_var.get():



            self._update_progress(95, self.t("install_step_registry"), "Registering file associations & context menus...")



            register_file_associations(main_exe, ico_dest, register_assoc=self.opt_assoc_var.get(), register_context=self.opt_context_var.get())



        # تسجيل البرنامج رسمياً في إعدادات ويندوز وقائمة التطبيقات المثبتة وRevo Uninstaller

        self._update_progress(98, self.t("install_step_registry"), "Registering uninstaller in Windows...")

        register_uninstaller_in_windows(dest, main_exe, ico_dest)







        time.sleep(0.3)



        self._update_progress(100, self.t("install_step_done"), "Done!")



        time.sleep(0.5)







        self.root.after(0, lambda: self.show_step(4))







    def _update_progress(self, pct, status_text, detail_text=""):



        def _apply():



            self.progress_bar["value"] = pct



            self.status_lbl.config(text=status_text)



            self.detail_lbl.config(text=detail_text)



        self.root.after(0, _apply)







    # --------------------------------------------------------------------------



    # الخطوة 5: اكتمال التثبيت بنجاح (Finished)



    # --------------------------------------------------------------------------



    def _render_step_finished(self):



        self.btn_cancel.pack_forget()



        self.btn_back.pack_forget()



        self.btn_next.pack(side="right", padx=16, pady=10)



        self.btn_next.config(text=self.t("btn_finish"), state="normal", command=self.on_finish)







        f_box = tk.Frame(self.content_frame, bg="#0c1017")



        f_box.pack(fill="both", expand=True, pady=10)







        # أيقونة التثبيت الكبيرة



        ico_large = self.icon_pil.resize((56, 56), Image.Resampling.LANCZOS)



        self.ico_large_tk = ImageTk.PhotoImage(ico_large)



        tk.Label(f_box, image=self.ico_large_tk, bg="#0c1017").pack(anchor="center", pady=(10, 8))







        fin_t = self.t("finish_title")
        fin_m = self.t("finish_msg")
        if getattr(self, "mode", "install") == "update":
            fin_t = self.t("update_done_title")
            fin_m = self.t("update_done_msg")
        elif getattr(self, "mode", "install") == "repair":
            fin_t = self.t("repair_done_title")
            fin_m = self.t("repair_done_msg")
        tk.Label(f_box, text=f"✔  {fin_t}",



                 bg="#0c1017", fg="#10b981", font=("Segoe UI", 14, "bold")).pack(anchor="center", pady=(0, 8))







        tk.Label(f_box, text=fin_m,



                 bg="#0c1017", fg="#cbd5e1", font=("Segoe UI", 10), justify="center").pack(anchor="center", pady=(0, 16))







        tk.Label(f_box, text="Developed exclusively by scar development",



                 bg="#0c1017", fg="#38bdf8", font=("Segoe UI", 9, "bold")).pack(anchor="center", pady=(0, 16))







        cb = tk.Checkbutton(f_box, text=self.t("opt_launch"), variable=self.launch_var,



                            bg="#0c1017", fg="#ffffff", selectcolor="#16202e",



                            activebackground="#0c1017", activeforeground="#38bdf8",



                            font=("Segoe UI", 10, "bold"))



        cb.pack(anchor="center", pady=4)







    def on_next(self):



        if self.current_step == 0:

            if self.installed_info:
                self.show_step("maintenance")
            else:
                self.show_step(1)



        elif self.current_step == 1:



            if not self.agree_var.get():



                messagebox.showwarning(self.t("title"), self.t("warn_agree"), parent=self.root)



                return



            self.show_step(2)



        elif self.current_step == 2:



            d = self.dest_dir_var.get().strip()



            if not d:



                messagebox.showwarning(self.t("title"), self.t("warn_dir"), parent=self.root)



                return



            self.show_step(3)







    def on_back(self):



        if self.current_step == "maintenance":
            self.show_step(0)

        elif isinstance(self.current_step, int) and self.current_step > 0:
            self.show_step(self.current_step - 1)







    def on_finish(self):



        dest = self.dest_dir_var.get()



        if self.launch_var.get():



            main_exe = os.path.join(dest, "SCAR RAR.exe")



            if os.path.exists(main_exe):



                subprocess.Popen([main_exe], cwd=dest)



            else:



                py_script = os.path.join(dest, "scarrar.py")



                if os.path.exists(py_script):



                    pythonw = sys.executable.lower().replace("python.exe", "pythonw.exe")
                    if not os.path.exists(pythonw): pythonw = sys.executable
                    subprocess.Popen([pythonw, py_script], cwd=dest)



        self.root.destroy()











if __name__ == "__main__":



    root = tk.Tk()



    app = ScarInstallerApp(root)



    root.mainloop()



