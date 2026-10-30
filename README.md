# ⚡ SCAR RAR — Next-Generation Archiving Tool

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.1.2-38bdf8?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTMgM2gxOHYxOEgzeiIgZmlsbD0iIzBjMTAxNyIvPjwvc3ZnPg==" alt="Version">
  <img src="https://img.shields.io/badge/platform-Windows%20|%20Linux%20|%20macOS-0066cc?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/license-Free%20Forever-22c55e?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/python-3.14-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

<p align="center">
  <b>A modern, lightning-fast, and elegant archive manager designed for power users, gamers, and modders.</b><br>
  Built with native high-speed engines, seamless OS integration, and a sleek Dark Obsidian interface.
</p>

<p align="center">
  <a href="#-key-features">Features</a> •
  <a href="#-supported-formats">Formats</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-installation--setup">Installation</a> •
  <a href="#-keyboard-shortcuts">Shortcuts</a> •
  <a href="#-built-with">Built With</a> •
  <a href="#-license--credits">License</a>
</p>

---

## 🌟 Key Features

### 🎨 Interface & Themes
- **Modern Dark Obsidian Interface** — Clean, distraction-free UI with ultra-smooth rendering and custom window chrome (no white title bars).
- **4 Built-in Themes** — Dark Obsidian, OLED Midnight Black, Cyber Cyan Dark, and Deep Royal Navy. Switch instantly from Options → Themes.
- **4 Languages** — Full localization in English, العربية (Arabic), Français (French), and Español (Spanish).

### ⚡ Performance & Engines
- **High-Speed Native Extraction & Compression** — Powered by official `UnRAR.exe` / `Rar.exe` binaries and optimized multithreaded engines for maximum throughput.
- **Maximum Compression** — Uses the "Best" compression method with solid archives and large dictionary sizes (up to 1024 MB) to achieve the smallest possible file sizes.
- **Real-Time Progress Dialogs** — Live byte-level tracking during extraction and compression with per-file progress, dynamic ETA countdown, elapsed time, compression ratio, and smooth progress bars.
- **Pause / Resume / Background** — Full control over running operations: pause, resume, run in background, or cancel at any time.
- **Transfer Rate Limiting** — Optional speed throttle (0–20,480 KB/s) for extraction and compression to keep your system responsive.

### 📦 Archive Operations
- **Create Archives** — RAR (with password + encrypted file names), ZIP, ISO (via IMAPI2), 7z, TAR/GZ/BZ2/XZ — all with a professional "Archive name and parameters" dialog inspired by WinRAR.
- **Extract Archives** — Extract Here, Extract to subfolder, or Extract to custom location with a full extraction path dialog, folder tree browser, and "New folder" support.
- **Multi-File Batch Archiving** — Select multiple files in Explorer → right-click → "Add to archive" and they are intelligently grouped into a single archive named after the parent folder (IPC-based process aggregation).
- **Test Archive Integrity** — Verify that all files in an archive are intact.
- **View Files** — Double-click to preview any file inside an archive with your default application.
- **Delete from Archive** — Remove individual files from ZIP archives.

### 🔒 Security
- **Encrypted Archive & Password Support** — Automatic detection of encrypted headers and password-protected archives with a dedicated dark-themed password dialog.
- **AES-256 Encryption** — Set passwords during archive creation with optional file name encryption.

### 🪟 Windows Shell Integration
- **Cascading Right-Click Context Menu** — Open, Extract Here, Extract to subfolder, Add to archive, Add to archive (RAR) — all with custom high-res SCAR RAR icons.
- **File Type Associations** — Register `.rar`, `.zip`, `.7z`, `.iso`, `.tar`, `.gz`, `.bz2`, `.xz` to open with SCAR RAR.
- **Seamless Clipboard Copy & Paste** — Press `Ctrl+C` on any file inside an archive, navigate to any folder, and press `Ctrl+V` to extract instantly.
- **Native OLE Drag & Drop** — Drag files out of archives directly into Windows Explorer or other applications.

### 🔄 Auto-Update System
- **Built-in Update Checker** — Checks GitHub Releases on startup and notifies you when a new version is available.
- **One-Click Download & Install** — Download updates directly from the app with a live progress dialog showing speed, size, and percentage. Launches the installer automatically when complete.

### 📚 Additional Features
- **Favorites System** — Bookmark frequently used archives and folders for instant access via the Favorites menu.
- **Settings Persistence** — Language, theme, favorites, window position, and preferences are saved across sessions.
- **Activity Log** — View and export a detailed log of all operations performed.
- **Built-in Help System** — Comprehensive interactive help catalog with topics for every feature.
- **File Manager Mode** — Browse your filesystem directly in SCAR RAR with directory listing, breadcrumb navigation, and toolbar actions.
- **About Dialog** — Shows version info, build details, and links to Discord and GitHub.

---

## 📦 Supported Formats

| Format | Read / Extract | Create / Compress |
|:------:|:--------------:|:-----------------:|
| **RAR** (RAR4 / RAR5 / SFX) | ✅ Yes | ✅ Yes |
| **ZIP** | ✅ Yes | ✅ Yes |
| **7-Zip (.7z)** | ✅ Yes | ✅ Yes |
| **TAR / GZ / BZ2 / XZ** | ✅ Yes | ✅ Yes |
| **ISO** (ISO 9660 / Joliet / UDF) | ✅ Yes | ✅ Yes |

---

## 📸 Screenshots

> Screenshots coming soon — SCAR RAR features a modern dark interface with custom window chrome, toolbar icons, and smooth animations.

---

## 🚀 Installation & Setup

### Windows (Recommended)

1. Download the latest installer from the **[Releases](https://github.com/zakariamahdjoubi03-cloud/Scar-Rar/releases)** page:
   - `SCAR.RAR.Setup.vX.X.X.exe`
2. Run the setup wizard — it will:
   - Install SCAR RAR to `C:\Program Files\SCAR RAR\`
   - Register file associations (`.rar`, `.zip`, `.7z`, `.iso`, `.tar`, `.gz`, `.bz2`, `.xz`)
   - Add cascading right-click context menus
   - Create Desktop and Start Menu shortcuts
3. Enjoy an ultra-fast, modern archiving experience!

### Linux

1. Download from the **[Releases](https://github.com/zakariamahdjoubi03-cloud/Scar-Rar/releases)** page:
   - **Debian/Ubuntu**: `scar-rar_X.X.X_amd64.deb`
   - **Other distros**: `scar-rar-X.X.X-linux-x86_64.tar.gz`
2. Install:
   ```bash
   # Debian / Ubuntu
   sudo dpkg -i scar-rar_X.X.X_amd64.deb

   # Other distros
   tar xzf scar-rar-X.X.X-linux-x86_64.tar.gz
   cd scar-rar-X.X.X
   ./install.sh
   ```
3. Launch from the application menu or run `scar-rar` from the terminal.

### macOS

1. Download from the **[Releases](https://github.com/zakariamahdjoubi03-cloud/Scar-Rar/releases)** page:
   - `SCAR.RAR-X.X.X-macOS.zip`
2. Extract and drag `SCAR RAR.app` to your **Applications** folder.
3. Launch from Launchpad or Spotlight.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|:--------:|:------:|
| `Ctrl+O` | Open archive |
| `Ctrl+C` | Copy selected files to clipboard |
| `Ctrl+V` | Paste / Extract files from clipboard |
| `Ctrl+A` | Select all files |
| `Delete` | Delete selected files from archive |
| `Enter` | Open / Extract selected file |
| `Backspace` | Navigate to parent directory |
| `F5` | Refresh file listing |
| `Alt+F4` | Close SCAR RAR |

---

## 🛠️ Built With

- **Python 3.14** & **Custom Tkinter / Win32 API Engine** — Native dark UI with DWM integration
- **Native UnRAR & Rar Binaries** — Official freeware engine by Alexander Roshal
- **IMAPI2FS COM API** — Native Windows ISO 9660/Joliet/UDF creation
- **Windows Libarchive (`bsdtar`)** & **PowerShell** — For 7z, TAR, and ISO operations
- **PyInstaller** — Standalone single-file deployment
- **Inno Setup-style Installer** — Custom dark-themed setup wizard with repair & uninstall

---

## 🗺️ Roadmap

- [ ] 7-Zip creation improvements
- [ ] Archive repair tool
- [ ] Batch extraction wizard
- [ ] Plugin / extension system
- [ ] Portable mode (no installation required)

---

## 🤝 Contributing & Feedback

Contributions, feature requests, and bug reports are welcome! Feel free to:
- 🐛 [Open an Issue](https://github.com/zakariamahdjoubi03-cloud/Scar-Rar/issues)
- 🔀 Submit a Pull Request
- 💬 Join the [Discord Community](https://discord.com/users/989509070908174406)

---

## ⚖️ License & Credits

Developed with ❤️ by **Scar Development** ([`zakariamahdjoubi03-cloud`](https://github.com/zakariamahdjoubi03-cloud)).

- SCAR RAR is **100% free forever** — no trial periods, no license nags, no tracking.
- UnRAR engine and WinRAR compression tools are copyrights of **Alexander L. Roshal**.
- All trademarks are property of their respective owners.
