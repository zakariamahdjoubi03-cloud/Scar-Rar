# -*- coding: utf-8 -*-
"""
================================================================================
SCAR RAR Help Catalog & Documentation System
Developed by: scar development
Copyright (c) 2026 scar development. All Rights Reserved.
================================================================================
"""

import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0

class HelpIcons:
    @staticmethod
    def get_icons():
        icons = {}
        # Book icon
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([1, 2, 14, 14], radius=2, fill="#0284c7", outline="#38bdf8")
        d.rectangle([3, 4, 12, 12], fill="#f8fafc")
        d.line([(5, 6), (10, 6)], fill="#0284c7")
        d.line([(5, 8), (10, 8)], fill="#0284c7")
        d.line([(5, 10), (9, 10)], fill="#0284c7")
        icons["book"] = ImageTk.PhotoImage(im)

        # Page / topic question icon
        im2 = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(im2)
        d2.polygon([(2, 1), (10, 1), (14, 5), (14, 15), (2, 15)], fill="#ffffff", outline="#64748b")
        d2.polygon([(10, 1), (10, 5), (14, 5)], fill="#cbd5e1", outline="#64748b")
        d2.text((5, 5), "?", fill="#0284c7")
        icons["page"] = ImageTk.PhotoImage(im2)

        def make_tb_icon(draw_func):
            img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw_func(draw)
            return ImageTk.PhotoImage(img)

        icons["hide"] = make_tb_icon(lambda d: (
            d.rectangle([1, 2, 6, 13], fill="#38bdf8", outline="#0284c7"),
            d.rectangle([8, 2, 14, 13], fill="#94a3b8", outline="#475569")
        ))
        icons["back"] = make_tb_icon(lambda d: (
            d.polygon([(4, 8), (10, 3), (10, 6), (14, 6), (14, 10), (10, 10), (10, 13)], fill="#22c55e", outline="#16a34a")
        ))
        icons["forward"] = make_tb_icon(lambda d: (
            d.polygon([(12, 8), (6, 3), (6, 6), (2, 6), (2, 10), (6, 10), (6, 13)], fill="#22c55e", outline="#16a34a")
        ))
        icons["print"] = make_tb_icon(lambda d: (
            d.rectangle([3, 5, 13, 11], fill="#64748b", outline="#334155"),
            d.rectangle([5, 1, 11, 5], fill="#f8fafc", outline="#94a3b8"),
            d.rectangle([5, 9, 11, 14], fill="#f8fafc", outline="#94a3b8")
        ))
        icons["options"] = make_tb_icon(lambda d: (
            d.ellipse([2, 2, 14, 14], fill="#0284c7", outline="#38bdf8"),
            d.line([(8, 4), (8, 12)], fill="#ffffff", width=2),
            d.line([(4, 8), (12, 8)], fill="#ffffff", width=2)
        ))

        return icons


HELP_TOPICS = {
    # id: (title_en, title_ar, parent_id, is_book, content_en, content_ar)
    "about": ("About SCAR RAR", "حول SCAR RAR", "", True, {
        "title": "About SCAR RAR",
        "desc": "SCAR RAR is a high-performance 64-bit archive manager developed by scar development.",
        "sections": [
            ("Overview", "SCAR RAR provides complete support for RAR and ZIP archives and is able to unpack and view CAB, ARJ, LZH, TAR, GZ, ACE, UUE, BZ2, JAR, ISO, 7Z, Z archives.\nIt consistently makes smaller archives than the competition, saving disk space and transmission costs."),
            ("Key Features", "• High-speed multithreaded decompression & compression\n• Integrated bandwidth limiter (Rate Limiter)\n• Native Windows OLE Drag & Drop\n• 100% Free / Freeware for personal and commercial use\n• Developed exclusively by scar development.")
        ]
    }, {
        "title": "حول برنامج SCAR RAR",
        "desc": "برنامج SCAR RAR هو مدير أرشيفات وضغط ملفات 64-بت عالي الأداء تم تطويره بواسطة scar development.",
        "sections": [
            ("نظرة عامة", "يوفر SCAR RAR دعماً شاملاً لأرشيفات RAR و ZIP وقادراً على استعراض واستخراج CAB, ARJ, LZH, TAR, GZ, ACE, UUE, BZ2, JAR, ISO, 7Z.\nيتميز بنسب ضغط استثنائية وسرعة فائقة في معالجة الملفات الضخمة."),
            ("الميزات الرئيسية", "• محرك فك وضغط متعدد المسارات وفائق السرعة\n• متحكم سرعة النقل والتحميل (Rate Limiter)\n• سحب وإفلات حقيقي أصيل لنظام ويندوز OLE DoDragDrop\n• مجاني بالكامل 100% للاستخدام الشخصي والتجاري\n• حيازة وحقوق ملكية حصرية لـ scar development.")
        ]
    }),

    "about_what": ("What is SCAR RAR", "ما هو SCAR RAR", "about", False, {
        "title": "What is SCAR RAR",
        "desc": "SCAR RAR is a Windows version of the RAR Archiver — a powerful tool which allows you to create, manage and control archive files.",
        "sections": [
            ("Key Advantages", "1. Complete support of RAR (including RAR 5.0) and ZIP archives.\n2. Sophisticated compression algorithm with special optimizations for multimedia, executables, and text.\n3. AES-256 bit encryption.\n4. Recovery records and recovery volumes.")
        ]
    }, {
        "title": "ما هو برنامج SCAR RAR",
        "desc": "SCAR RAR هو الجيل الحديث من برامج إدارة الأرشيفات لنظام ويندوز — أداة قوية تتيح إنشاء وإدارة والتحكم في الملفات المضغوطة بكفاءة عالية.",
        "sections": [
            ("أهم المزايا", "1. دعم كامل لصيغ RAR (بما في ذلك RAR 5.0) و ZIP.\n2. خوارزميات ضغط متقدمة ومحسنة للوسائط والبرمجيات والنصوص.\n3. تشفير فائق القوة AES-256.\n4. سجلات الاسترداد واستعادة الأرشيفات المتضررة.")
        ]
    }),

    "about_limits": ("SCAR RAR limitations", "حدود ومواصفات SCAR RAR", "about", False, {
        "title": "SCAR RAR limitations",
        "desc": "Technical boundaries and specifications of SCAR RAR archives.",
        "sections": [
            ("Archive Size", "Practically unlimited (up to 8,589,934,591 GB in RAR 5.0 format)."),
            ("Number of Files", "Unlimited number of files in an archive."),
            ("Path Length", "Supports Windows long path names up to 32,767 characters.")
        ]
    }, {
        "title": "حدود ومواصفات SCAR RAR",
        "desc": "المواصفات التقنية والحدود التشغيلية لأرشيفات SCAR RAR.",
        "sections": [
            ("حجم الأرشيف", "غير محدود عملياً (حتى 8.5 مليار جيجابايت في صيغة RAR 5.0)."),
            ("عدد الملفات", "عدد غير محدود من الملفات داخل الأرشيف الواحد."),
            ("طول المسارات", "دعم المسارات الطويلة في ويندوز حتى 32,767 حرفاً.")
        ]
    }),

    "about_ack": ("Acknowledgements & scar development", "شكر وتقدير وحقوق scar development", "about", False, {
        "title": "Acknowledgements",
        "desc": "SCAR RAR was engineered with passion by scar development.\nCopyright (c) 2026 scar development. All Rights Reserved.\nDiscord Profile: https://discord.com/users/989509070908174406",
        "sections": [
            ("License", "100% Free / Freeware for Personal and Commercial Use.")
        ]
    }, {
        "title": "شكر وتقدير وحقوق التطوير",
        "desc": "تم تصميم وهندسة SCAR RAR بشغف واحترافية بواسطة scar development.\nجميع الحقوق محفوظة (c) 2026 scar development.\nالملف الشخصي على ديسكورد: https://discord.com/users/989509070908174406",
        "sections": [
            ("الترخيص", "مجاني 100% للاستخدام الشخصي والتجاري مدى الحياة.")
        ]
    }),

    # Quick start
    "quick": ("Quick start for novices", "البداية السريعة للمبتدئين", "", True, {
        "title": "Quick start for novices",
        "desc": "A beginner's guide to using SCAR RAR in everyday file management.",
        "sections": [
            ("Two Operating Modes", "SCAR RAR operates in two basic modes: graphical interactive interface and Windows shell context menu integration.")
        ]
    }, {
        "title": "البداية السريعة للمبتدئين",
        "desc": "دليل المبتدئين لاستخدام برنامج SCAR RAR في إدارة وضغط الملفات اليومية.",
        "sections": [
            ("نمطا التشغيل", "يعمل البرنامج بنمطين أساسيين: الواجهة الرسومية التفاعلية، والتكامل مع قائمة الزر الأيمن في نظام ويندوز.")
        ]
    }),

    "quick_extract": ("How to extract files", "طريقة استخراج الملفات", "quick", True, {
        "title": "How to extract files",
        "desc": "Instructions on extracting compressed archives.",
        "sections": [
            ("Methods", "You can extract files using the main window 'Extract To' button, right-click context menu 'Extract files...', or Drag & Drop directly to any folder or desktop.")
        ]
    }, {
        "title": "طريقة استخراج وفك ضغط الملفات",
        "desc": "إرشادات استخراج وفك ضغط الملفات بمرونة وسرعة.",
        "sections": [
            ("طرق الاستخراج", "يمكن استخراج الملفات عبر زر 'Extract To' في الواجهة، أو بالزر الأيمن بالفأرة 'Extract files...'، أو عبر السحب والإفلات المباشر إلى سطح المكتب أو أي مجلد.")
        ]
    }),

    "quick_extract_gui": ("How to extract files using SCAR RAR", "استخراج الملفات عبر واجهة SCAR RAR", "quick_extract", False, {
        "title": "How to extract files using SCAR RAR",
        "desc": "1. Open the archive in SCAR RAR.\n2. Click the 'Extract To' button on the toolbar or press Alt+E.\n3. In the 'Extraction path and options' dialog, choose your destination folder.\n4. Configure options on General, Advanced, or Options tabs if desired.\n5. Click OK.",
        "sections": []
    }, {
        "title": "استخراج الملفات عبر واجهة SCAR RAR",
        "desc": "1. افتح الأرشيف المطلوب في SCAR RAR.\n2. اضغط على زر 'Extract To' (استخراج إلى) في شريط الأدوات أو Alt+E.\n3. حدد مسار الاستخراج المطلوب في نافذة الخيارات.\n4. اختر أي خيارات إضافية في تبويبات General أو Advanced أو Options.\n5. اضغط على موافق (OK).",
        "sections": []
    }),

    "quick_extract_ctx": ("How to extract files using context menu", "استخراج الملفات عبر كليك يمين", "quick_extract", False, {
        "title": "How to extract files using context menu",
        "desc": "Right-click any archive file (.rar, .zip, .7z) in Windows Explorer:\n• Extract files...: Opens the extraction options dialog.\n• Extract Here: Extracts all files into the current folder.\n• Extract to <Folder>: Extracts into a newly created subfolder with archive name.",
        "sections": []
    }, {
        "title": "استخراج الملفات عبر قائمة الزر الأيمن (كليك يمين)",
        "desc": "انقر بالزر الأيمن على أي ملف مضغوط في ويندوز:\n• Extract files...: يفتح نافذة خيارات الاستخراج لتحديد المسار بحرية.\n• Extract Here: يستخرج الملفات مباشرة في نفس المجلد الحالي.\n• Extract to <Folder>: ينشئ مجلداً باسم الأرشيف ويستخرج الملفات بداخله.",
        "sections": []
    }),

    "quick_extract_dnd": ("How to extract files using Drag and Drop", "استخراج الملفات عبر السحب والإفلات (Drag & Drop)", "quick_extract", False, {
        "title": "How to extract files using Drag and Drop",
        "desc": "1. Open any archive in SCAR RAR.\n2. Select one or more files or folders in the archive list.\n3. Hold the left mouse button down and drag the selected items to your Desktop or any open folder in Windows Explorer.\n4. Release the mouse button. SCAR RAR automatically extracts the items directly to that location!",
        "sections": []
    }, {
        "title": "استخراج الملفات عبر السحب والإفلات (Drag and Drop)",
        "desc": "1. افتح أي أرشيف داخل SCAR RAR.\n2. حدد الملفات أو المجلدات المطلوبة داخل القائمة.\n3. اضغط مع الاستمرار بالزر الأيسر للفأرة واسحب الملفات خارج النافذة نحو سطح المكتب أو أي مجلد في ويندوز.\n4. أفلت زر الفأرة. يقوم SCAR RAR فوراً باستخراج الملفات مباشرة إلى المكان الذي أفلته فيه!",
        "sections": []
    }),

    # Toolbar buttons
    "interface": ("SCAR RAR interface", "واجهة برنامج SCAR RAR وأزرارها", "", True, {
        "title": "SCAR RAR interface",
        "desc": "Explanation of SCAR RAR main window, toolbar, and controls.",
        "sections": [
            ("Overview", "The interface consists of the Title Bar, Menu Bar, Quick Toolbar, Address Bar, File List Treeview, and Status Bar.")
        ]
    }, {
        "title": "واجهة برنامج SCAR RAR وأزرارها",
        "desc": "شرح تفصيلي لكافة أزرار ومكونات واجهة SCAR RAR.",
        "sections": [
            ("نظرة عامة", "تتكون الواجهة من شريط العنوان العصري، شريط القوائم، شريط الأدوات الرئيسي، شريط المسار، قائمة الملفات الشجرية، وشريط الحالة السفلي.")
        ]
    }),

    "btn_open": ("Open button", "زر الفتح (Open)", "interface", False, {
        "title": "Open button (Ctrl+O)",
        "desc": "Opens an archive file selection dialog allowing you to browse and open any supported archive format (.rar, .zip, .7z, .iso, .tar, .gz, etc.).",
        "sections": []
    }, {
        "title": "زر الفتح Open (اختصار Ctrl+O)",
        "desc": "يفتح نافذة استعراض واختيار الملفات لفتح وتصفح أي أرشيف مضغوط (.rar, .zip, .7z, .iso, .tar, إلخ).",
        "sections": []
    }),

    "btn_add": ("Add button", "زر الإضافة والضغط (Add)", "interface", False, {
        "title": "Add to archive button (Alt+A)",
        "desc": "Compresses selected files or folders into a new or existing RAR, ZIP, or TAR archive.\nAllows configuring compression level, archive format, and password protection.",
        "sections": []
    }, {
        "title": "زر الإضافة والضغط Add (اختصار Alt+A)",
        "desc": "يقوم بضغط الملفات أو المجلدات المحددة في أرشيف جديد أو قائم بصيغ RAR أو ZIP أو TAR مع خيارات التشفير ونسب الضغط.",
        "sections": []
    }),

    "btn_extract": ("Extract To button", "زر الاستخراج (Extract To)", "interface", False, {
        "title": "Extract To button (Alt+E)",
        "desc": "Opens the 'Extraction path and options' dialog where you can set destination folder, update modes, overwrite modes, and advanced switches.",
        "sections": []
    }, {
        "title": "زر الاستخراج Extract To (اختصار Alt+E)",
        "desc": "يفتح نافذة 'Extraction path and options' الشاملة لتحديد مجلد الوجهة، ونمط التحديث، واستبدال الملفات، وخيارات الطاقة والإغلاق التلقائي.",
        "sections": []
    }),

    "btn_test": ("Test button", "زر الفحص والاختبار (Test)", "interface", False, {
        "title": "Test button (Alt+T)",
        "desc": "Tests the integrity of the currently open archive by verifying CRCs and unpacking data in memory to ensure no files are corrupted.",
        "sections": []
    }, {
        "title": "زر الفحص والاختبار Test (اختصار Alt+T)",
        "desc": "يقوم بفحص سلامة الأرشيف المفتوح والتأكد من عدم وجود أي تلف أو بيانات معطوبة عبر التحقق من سجلات CRC في الذاكرة.",
        "sections": []
    }),

    "btn_view": ("View button", "زر العرض السريع (View)", "interface", False, {
        "title": "View button (Alt+V)",
        "desc": "Opens the currently selected archived file in the internal viewer or registered default Windows application without manually extracting it.",
        "sections": []
    }, {
        "title": "زر العرض السريع View (اختصار Alt+V)",
        "desc": "يعرض محتوى الملف المحدد داخل الأرشيف مباشرة دون الحاجة لفك ضغطه يدوياً إلى القرص.",
        "sections": []
    }),

    "btn_delete": ("Delete button", "زر الحذف (Delete)", "interface", False, {
        "title": "Delete button (Del)",
        "desc": "Deletes selected files or folders from the archive with a confirmation prompt.",
        "sections": []
    }, {
        "title": "زر الحذف Delete (زر Del)",
        "desc": "يحذف الملفات أو المجلدات المحددة من داخل الأرشيف مع رسالة تأكيد لحماية بياناتك.",
        "sections": []
    }),

    "btn_find": ("Find button", "زر البحث (Find)", "interface", False, {
        "title": "Find button (Alt+I)",
        "desc": "Searches for file names or text strings inside archives and directories.",
        "sections": []
    }, {
        "title": "زر البحث Find (اختصار Alt+I)",
        "desc": "يتيح البحث السريع عن أسماء الملفات أو النصوص داخل الأرشيفات والمجلدات.",
        "sections": []
    }),

    "btn_wizard": ("Wizard button", "زر المعالج الذكي (Wizard)", "interface", False, {
        "title": "Wizard button",
        "desc": "Step-by-step assistant for novice users to unpack or create archives easily.",
        "sections": []
    }, {
        "title": "زر المعالج الذكي Wizard",
        "desc": "مساعد خطوة بخطوة للمستخدمين المبتدئين لضغط أو فك ضغط الأرشيفات بسهولة وسلاسة.",
        "sections": []
    }),

    "btn_info": ("Info button", "زر الخصائص والمعلومات (Info)", "interface", False, {
        "title": "Info button (Alt+I)",
        "desc": "Displays detailed archive properties, total files, uncompressed size, packed size, compression ratio, dictionary size, and encryption status.",
        "sections": []
    }, {
        "title": "زر الخصائص والمعلومات Info (اختصار Alt+I)",
        "desc": "يعرض تفاصيل شاملة عن الأرشيف: الحجم الأصلي، الحجم المضغوط، نسبة التوفير، عدد الملفات، وحالة التشفير.",
        "sections": []
    }),

    "btn_discord": ("Discord button", "زر دعم ديسكورد (Discord)", "interface", False, {
        "title": "Discord Support button",
        "desc": "Instantly opens the official developer Discord profile: https://discord.com/users/989509070908174406 for updates and technical support.",
        "sections": []
    }, {
        "title": "زر دعم وتواصل ديسكورد Discord",
        "desc": "يفتح فوراً الملف الشخصي للمطور على ديسكورد: https://discord.com/users/989509070908174406 لتقديم الدعم الفني وتلقي الاقتراحات والتحديثات.",
        "sections": []
    }),

    # Command line mode
    "cmd": ("Command line mode", "أوامر سطر الأوامر (Command Line)", "", True, {
        "title": "Command line mode",
        "desc": "SCAR RAR supports standard WinRAR-compatible command line syntax:\nscarrar <command> -<switch 1> -<switch N> <archive> <files...>",
        "sections": []
    }, {
        "title": "أوامر سطر الأوامر (Command Line)",
        "desc": "يدعم SCAR RAR صيغة أوامر WinRAR القياسية في الطرفية وسطر الأوامر:\nscarrar <command> -<switch 1> -<switch N> <archive> <files...>",
        "sections": []
    }),

    "cmd_x": ("Command X - extract files with full paths", "الأمر X - استخراج الملفات مع مساراتها الكاملة", "cmd", False, {
        "title": "Command X - extract files from an archive with full paths",
        "desc": "Extract files and folder with full paths. The folder structure, saved in the archive, is completely restored. This is the command line equivalent of the archive management command Extract To.",
        "sections": [
            ("Syntax & Examples", "scarrar x Fonts *.ttf\nExtracts all *.ttf files from archive Fonts to the current folder, restoring full folder tree.\n\nscarrar x Fonts *.ttf NewFonts\\\nExtracts all *.ttf files from the archive Fonts to the folder NewFonts\\\n\nYou need to use the trailing backslash as in the example above for denoting the destination folder.")
        ]
    }, {
        "title": "الأمر X - استخراج الملفات بالمسارات الكاملة",
        "desc": "يستخرج الملفات والمجلدات مع الحفاظ التام على هيكل المجلدات والمسارات المحفوظة بالأرشيف. وهو المكافئ لزر Extract To في الواجهة.",
        "sections": [
            ("أمثلة الاستخدام", "scarrar x Fonts *.ttf\nيستخرج ملفات الخطوط إلى المجلد الحالي مع الحفاظ على المجلدات الفرعية.\n\nscarrar x Fonts *.ttf NewFonts\\\nيستخرج الخطوط إلى المجلد المحدد NewFonts\\ مع بناء الشجرة الأصلية.")
        ]
    }),

    "cmd_e": ("Command E - extract files ignoring paths", "الأمر E - استخراج الملفات متجاهلاً المسارات", "cmd", False, {
        "title": "Command E - extract files ignoring paths",
        "desc": "Extracts files to the destination directory without recreating folder hierarchies. All unpacked files will be placed into the same single directory.",
        "sections": [
            ("Syntax & Examples", "scarrar e archive.rar c:\\dest\\\nUnpacks all files flatly into c:\\dest\\ without creating subfolders.")
        ]
    }, {
        "title": "الأمر E - استخراج الملفات متجاهلاً المسارات",
        "desc": "يستخرج كافة الملفات داخل الأرشيف إلى مجلد الوجهة مباشرة دون إنشاء مجلدات فرعية (استخراج مسطح Flat Extraction).",
        "sections": [
            ("مثال الاستخدام", "scarrar e archive.rar c:\\dest\\\nيفرغ جميع الملفات في c:\\dest\\ دون أي مجلدات فرعية.")
        ]
    }),

    "cmd_a": ("Command A - add files to an archive", "الأمر A - ضغط وإضافة ملفات للأرشيف", "cmd", False, {
        "title": "Command A - add files to an archive",
        "desc": "Adds specified files and folders to an archive.",
        "sections": [
            ("Syntax & Examples", "scarrar a backup.rar c:\\data\\*\nAdds all files in c:\\data\\ to backup.rar.")
        ]
    }, {
        "title": "الأمر A - ضغط وإضافة ملفات للأرشيف",
        "desc": "يقوم بإنشاء أو تحديث أرشيف وإضافة ملفات ومجلدات إليه.",
        "sections": [
            ("مثال الاستخدام", "scarrar a backup.rar c:\\data\\*\nيضيف كافة ملفات c:\\data\\ إلى الأرشيف backup.rar.")
        ]
    }),

    "cmd_t": ("Command T - test archive files", "الأمر T - فحص سلامة الأرشيف", "cmd", False, {
        "title": "Command T - test archive files",
        "desc": "Tests the integrity of archived files without writing anything to disk.",
        "sections": [
            ("Syntax & Examples", "scarrar t backup.rar\nVerifies all CRCs and checksums.")
        ]
    }, {
        "title": "الأمر T - فحص واختبار سلامة الأرشيف",
        "desc": "يفحص الأرشيف ويتحقق من سلامة كافة البيانات والتوقيعات الرقمية دون الكتابة على القرص.",
        "sections": [
            ("مثال الاستخدام", "scarrar t backup.rar\nيتحقق من سلامة جميع محتويات backup.rar.")
        ]
    }),

    # Switches
    "switches": ("Switches list", "قائمة مفاتيح الأوامر (Switches)", "cmd", True, {
        "title": "Command line switches",
        "desc": "Alphabetical switches modifying command operations.",
        "sections": []
    }, {
        "title": "قائمة مفاتيح الأوامر (Switches)",
        "desc": "المفاتيح والمحددات الإضافية للتحكم بسلوك الأوامر.",
        "sections": []
    }),

    "sw_p": ("-p[pwd] - set password", "-p[pwd] - تعيين كلمة المرور", "switches", False, {
        "title": "-p[pwd] - set password",
        "desc": "Specifies a password when encrypting or extracting protected archives.",
        "sections": []
    }, {
        "title": "-p[pwd] - تعيين كلمة المرور",
        "desc": "تحديد كلمة السر للتشفير أو لفك تشفير الأرشيفات المحمية.",
        "sections": []
    }),

    "sw_hp": ("-hp[pwd] - encrypt headers", "-hp[pwd] - تشفير البيانات وأسماء الملفات", "switches", False, {
        "title": "-hp[pwd] - encrypt both file data and headers",
        "desc": "Encrypts both file data and archive directory headers, making file names invisible without password.",
        "sections": []
    }, {
        "title": "-hp[pwd] - تشفير البيانات وأسماء الملفات",
        "desc": "يشفر البيانات ورؤوس الأرشيف، بحيث لا يمكن حتى رؤية أسماء الملفات إلا بعد إدخال كلمة السر.",
        "sections": []
    }),

    "sw_o": ("-o[+|-] - set overwrite mode", "-o[+|-] - تحديد نمط استبدال الملفات", "switches", False, {
        "title": "-o[+|-] - set overwrite mode",
        "desc": "-o+ : Overwrite existing files without prompt.\n-o- : Skip existing files without prompt.",
        "sections": []
    }, {
        "title": "-o[+|-] - نمط الاستبدال التلقائي",
        "desc": "-o+ : استبدال الملفات الموجودة مسبقاً دون سؤال.\n-o- : تخطي الملفات الموجودة دون سؤال.",
        "sections": []
    }),

    "sw_kb": ("-kb - keep broken extracted files", "-kb - الاحتفاظ بالملفات التالفة", "switches", False, {
        "title": "-kb - keep broken extracted files",
        "desc": "Prevents SCAR RAR from deleting files that were only partially extracted due to CRC errors.",
        "sections": []
    }, {
        "title": "-kb - الاحتفاظ بالملفات المستخرجة المعطوبة",
        "desc": "يمنع البرنامج من حذف الملفات التي تم استخراج جزء منها عند حدوث خطأ CRC للاستفادة منها.",
        "sections": []
    }),

    "sw_ibck": ("-ibck - background extraction", "-ibck - التشغيل في الخلفية", "switches", False, {
        "title": "-ibck - run in background",
        "desc": "Runs the extraction or compression operation minimized in the Windows background.",
        "sections": []
    }, {
        "title": "-ibck - التشغيل الصامت في الخلفية",
        "desc": "تنفيذ عملية الاستخراج أو الضغط في الخلفية بأقل استهلاك لموارد المعالج.",
        "sections": []
    }),

    "sw_m": ("-m<0..5> - set compression level", "-m<0..5> - تحديد مستوى الضغط", "switches", False, {
        "title": "-m<0..5> - set compression level",
        "desc": "0: Store (no compression)\n1: Fastest\n2: Fast\n3: Normal (default)\n4: Good\n5: Best (maximum compression)",
        "sections": []
    }, {
        "title": "-m<0..5> - تحديد مستوى الضغط",
        "desc": "0: تخزين بدون ضغط (Store)\n1: الأسرع (Fastest)\n2: سريع (Fast)\n3: عادي افتراضي (Normal)\n4: جيد (Good)\n5: أقصى ضغط ممكن (Best)",
        "sections": []
    })
}


class ScarHelpCatalogDialog:
    def __init__(self, parent=None, initial_topic="cmd_x", app=None):
        self.parent = parent
        self.app = app
        self.lang = "ar" if (app and getattr(app, "current_lang", "") == "العربية") else "en"
        self.current_topic = initial_topic
        self.history = [initial_topic]
        self.history_idx = 0

        self.win = tk.Toplevel(parent) if parent else tk.Tk()
        title_txt = "مساعدة SCAR RAR" if self.lang == "ar" else "SCAR RAR Help"
        self.win.title(title_txt)
        self.win.geometry("940x630")
        self.win.minsize(700, 450)
        self.win.configure(bg="#f8fafc")

        if parent:
            try:
                self.win.transient(parent)
            except Exception:
                pass

        self.icons = HelpIcons.get_icons()
        self._pane_hidden = False
        self._setting_selection = False

        self._build_toolbar()
        self._build_main_ui()
        self._populate_tree()
        self._select_topic(initial_topic, add_history=False)
        self._center(940, 630)

    def _center(self, w, h):
        try:
            sw = self.win.winfo_screenwidth()
            sh = self.win.winfo_screenheight()
            if self.parent and hasattr(self.parent, "state") and self.parent.state() != "withdrawn" and self.parent.winfo_width() > 100:
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

    def _build_toolbar(self):
        tb_frame = tk.Frame(self.win, bg="#f1f5f9", height=42, bd=0, highlightbackground="#cbd5e1", highlightthickness=1)
        tb_frame.pack(side="top", fill="x")

        def make_btn(text_en, text_ar, icon_k, cmd):
            txt = text_ar if self.lang == "ar" else text_en
            btn_f = tk.Frame(tb_frame, bg="#f1f5f9", padx=4, pady=2)
            btn_f.pack(side="left" if self.lang != "ar" else "right", padx=2)
            btn = tk.Button(
                btn_f, text=f" {txt}", image=self.icons.get(icon_k), compound="left",
                command=cmd, bg="#f1f5f9", fg="#1e293b", activebackground="#e2e8f0",
                activeforeground="#0f172a", relief="flat", bd=0, padx=8, pady=3,
                font=("Segoe UI", 9), cursor="hand2"
            )
            btn.pack()
            return btn

        self.btn_hide = make_btn("Hide", "إخفاء", "hide", self._toggle_nav_pane)
        self.btn_back = make_btn("Back", "رجوع", "back", self._on_back)
        self.btn_forward = make_btn("Forward", "تقدم", "forward", self._on_forward)
        self.btn_print = make_btn("Print", "طباعة", "print", self._on_print)
        self.btn_options = make_btn("Options", "خيارات", "options", self._on_options)

    def _toggle_nav_pane(self):
        if self._pane_hidden:
            side_pack = "left" if self.lang != "ar" else "right"
            self.left_pane.pack(side=side_pack, fill="y", before=self.sep)
            txt = " إخفاء" if self.lang == "ar" else " Hide"
            self.btn_hide.config(text=txt)
            self._pane_hidden = False
        else:
            self.left_pane.pack_forget()
            txt = " إظهار" if self.lang == "ar" else " Show"
            self.btn_hide.config(text=txt)
            self._pane_hidden = True

    def _on_back(self):
        if self.history_idx > 0:
            self.history_idx -= 1
            topic = self.history[self.history_idx]
            self._select_topic(topic, add_history=False)

    def _on_forward(self):
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            topic = self.history[self.history_idx]
            self._select_topic(topic, add_history=False)

    def _on_print(self):
        try:
            txt = self.txt_view.get("1.0", "end")
            self.win.clipboard_clear()
            self.win.clipboard_append(txt)
        except Exception:
            pass

    def _on_options(self):
        pass

    def _build_main_ui(self):
        container = tk.Frame(self.win, bg="#ffffff")
        container.pack(fill="both", expand=True)

        side_left = "left" if self.lang != "ar" else "right"
        side_right = "right" if self.lang != "ar" else "left"

        # Left pane (Tabs: Contents, Index, Search, Favorites)
        self.left_pane = tk.Frame(container, bg="#f8fafc", width=280)
        self.left_pane.pack(side=side_left, fill="y")
        self.left_pane.pack_propagate(False)

        self.nb = ttk.Notebook(self.left_pane)
        self.nb.pack(fill="both", expand=True)

        tab_contents = tk.Frame(self.nb, bg="#ffffff")
        tab_search = tk.Frame(self.nb, bg="#ffffff")
        
        c_title = "المحتويات" if self.lang == "ar" else "Contents"
        s_title = "البحث" if self.lang == "ar" else "Search"
        self.nb.add(tab_contents, text=f" {c_title} ")
        self.nb.add(tab_search, text=f" {s_title} ")

        # Treeview in contents
        tree_f = tk.Frame(tab_contents, bg="#ffffff")
        tree_f.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_f, show="tree", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        sb_tree = ttk.Scrollbar(tree_f, orient="vertical", command=self.tree.yview)
        sb_tree.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb_tree.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_selected)

        # Search tab UI
        s_box = tk.Frame(tab_search, bg="#ffffff", padx=6, pady=6)
        s_box.pack(fill="x")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        ent_s = tk.Entry(s_box, textvariable=self.search_var, font=("Segoe UI", 9))
        ent_s.pack(fill="x", ipady=3)

        self.search_list = tk.Listbox(tab_search, bd=0, highlightthickness=0, font=("Segoe UI", 9))
        self.search_list.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.search_list.bind("<<ListboxSelect>>", self._on_search_select)

        # Separator line
        self.sep = tk.Frame(container, bg="#cbd5e1", width=1)
        self.sep.pack(side=side_left, fill="y")

        # Right pane (Reading View)
        self.right_pane = tk.Frame(container, bg="#ffffff")
        self.right_pane.pack(side=side_left, fill="both", expand=True)

        self.txt_view = tk.Text(
            self.right_pane, wrap="word", bg="#ffffff", fg="#0f172a",
            padx=28, pady=22, bd=0, highlightthickness=0, font=("Segoe UI", 9)
        )
        self.txt_view.pack(side="left", fill="both", expand=True)

        sb_txt = ttk.Scrollbar(self.right_pane, orient="vertical", command=self.txt_view.yview)
        sb_txt.pack(side="right", fill="y")
        self.txt_view.configure(yscrollcommand=sb_txt.set)

        # Text styles
        self.txt_view.tag_configure("title", font=("Segoe UI", 15, "bold"), foreground="#0066cc", spacing3=12)
        self.txt_view.tag_configure("desc", font=("Segoe UI", 10), foreground="#1e293b", spacing3=10)
        self.txt_view.tag_configure("sec_h", font=("Segoe UI", 11, "bold"), foreground="#0066cc", spacing1=14, spacing3=4)
        self.txt_view.tag_configure("sec_b", font=("Segoe UI", 9), foreground="#334155", spacing3=8)
        self.txt_view.tag_configure("code", font=("Consolas", 10, "bold"), foreground="#0f172a", background="#f1f5f9")

    def _populate_tree(self):
        for tid, data in HELP_TOPICS.items():
            title_en, title_ar, pid, is_book, c_en, c_ar = data
            title = title_ar if self.lang == "ar" else title_en
            img = self.icons.get("book" if is_book else "page")
            self.tree.insert(pid, "end", iid=tid, text=f" {title}", image=img, open=True)

    def _on_search_change(self, *args):
        query = self.search_var.get().strip().lower()
        self.search_list.delete(0, "end")
        self._search_map = []
        if not query:
            return
        for tid, data in HELP_TOPICS.items():
            title_en, title_ar, pid, is_book, c_en, c_ar = data
            content = c_ar if self.lang == "ar" else c_en
            title = title_ar if self.lang == "ar" else title_en
            full_txt = (title + " " + content.get("desc", "")).lower()
            if query in full_txt:
                self.search_list.insert("end", title)
                self._search_map.append(tid)

    def _on_search_select(self, event):
        if getattr(self, "_setting_selection", False):
            return
        sel = self.search_list.curselection()
        if sel and hasattr(self, "_search_map"):
            idx = sel[0]
            if idx < len(self._search_map):
                tid = self._search_map[idx]
                if tid != getattr(self, "current_topic", None):
                    self._select_topic(tid, add_history=True)

    def _on_tree_selected(self, event):
        if getattr(self, "_setting_selection", False):
            return
        sel = self.tree.selection()
        if sel:
            tid = sel[0]
            if tid != getattr(self, "current_topic", None):
                self._select_topic(tid, add_history=True)

    def _select_topic(self, topic_id, add_history=True):
        if topic_id not in HELP_TOPICS:
            return
        self.current_topic = topic_id
        if add_history:
            self.history = self.history[:self.history_idx + 1]
            self.history.append(topic_id)
            self.history_idx = len(self.history) - 1

        title_en, title_ar, pid, is_book, c_en, c_ar = HELP_TOPICS[topic_id]
        data = c_ar if self.lang == "ar" else c_en

        self._setting_selection = True
        try:
            self.tree.selection_set(topic_id)
            self.tree.see(topic_id)
        except Exception:
            pass
        finally:
            self._setting_selection = False

        self.txt_view.config(state="normal")
        self.txt_view.delete("1.0", "end")

        self.txt_view.insert("end", data["title"] + "\n", "title")
        self.txt_view.insert("end", data["desc"] + "\n\n", "desc")

        for sec_title, sec_content in data.get("sections", []):
            self.txt_view.insert("end", sec_title + "\n", "sec_h")
            lines = sec_content.splitlines()
            for l in lines:
                if l.startswith("scarrar") or l.startswith("WinRAR"):
                    self.txt_view.insert("end", "  " + l + "\n", "code")
                else:
                    self.txt_view.insert("end", l + "\n", "sec_b")
            self.txt_view.insert("end", "\n")

        self.txt_view.config(state="disabled")
