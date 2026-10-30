# -*- coding: utf-8 -*-
import os
import sys
import io
import time
import tarfile
import zipfile
import shutil
import struct
from PIL import Image

VERSION = "1.1.2"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
os.makedirs(DIST_DIR, exist_ok=True)

# 1. Generate high-res 256x256 PNG icon
icon_png_path = os.path.join(DIST_DIR, "scarrar.png")
ico_path = os.path.join(ROOT_DIR, "scarrar_icon.ico")
if os.path.exists(ico_path):
    img = Image.open(ico_path)
    img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
    img_256.save(icon_png_path, format="PNG")
else:
    img = Image.new("RGBA", (256, 256), (13, 35, 58, 255))
    img.save(icon_png_path, format="PNG")
print(f"Generated icon: {icon_png_path}")

# 2. Generate Apple ICNS
icns_path = os.path.join(DIST_DIR, "AppIcon.icns")
def make_icns(png_p, out_p):
    src = Image.open(png_p).convert("RGBA")
    buf = io.BytesIO()
    buf.write(b"icns\x00\x00\x00\x00")
    for tag, sz in [(b"ic07", (128, 128)), (b"ic08", (256, 256)), (b"ic09", (512, 512))]:
        r = src.resize(sz, Image.Resampling.LANCZOS)
        b = io.BytesIO()
        r.save(b, format="PNG")
        d = b.getvalue()
        buf.write(tag + struct.pack(">I", len(d) + 8) + d)
    tot = buf.tell()
    buf.seek(4)
    buf.write(struct.pack(">I", tot))
    with open(out_p, "wb") as f:
        f.write(buf.getvalue())
make_icns(icon_png_path, icns_path)
print(f"Generated macOS ICNS: {icns_path}")

# Common source files to pack
src_files = [
    "scarrar.py",
    "scar_help.py",
    "scarrar_favorites.json",
    "scarrar_icon.ico"
]

# ==============================================================================
# LINUX BUILD (DEB + PORTABLE TAR.GZ)
# ==============================================================================
print("\n--- Building Linux Packages ---")

# A. Linux Desktop file
desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=SCAR RAR
GenericName=Archive Manager
Comment=Modern, High-Performance Archiving & Extraction Tool
Exec=scarrar %F
Icon=scarrar
Terminal=false
Categories=Utility;Archiving;Compression;
MimeType=application/x-rar;application/vnd.rar;application/zip;application/x-7z-compressed;application/x-tar;application/x-iso9660-image;
Keywords=rar;zip;tar;7z;iso;archive;extract;compress;
StartupNotify=true
Actions=Add;Extract;

[Desktop Action Add]
Name=Add to archive...
Exec=scarrar -a %F

[Desktop Action Extract]
Name=Extract here
Exec=scarrar -x %F
"""

# B. Linux Runner Script
linux_runner_content = """#!/usr/bin/env bash
# SCAR RAR Linux Unified Launcher
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
APP_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

if [ -d "/usr/share/scarrar" ]; then
    APP_DIR="/usr/share/scarrar"
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3 is required to run SCAR RAR."
    exit 1
fi

export PYTHONPATH="$APP_DIR:$PYTHONPATH"
exec python3 "$APP_DIR/scarrar.py" "$@"
"""

# C. Linux Installer Script (for tar.gz)
linux_install_sh = f"""#!/usr/bin/env bash
# ==============================================================================
# SCAR RAR Linux Installer (v{VERSION})
# ==============================================================================
set -e

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

echo -e "${{BLUE}}===============================================${{NC}}"
echo -e "${{GREEN}}       Installing SCAR RAR v{VERSION} on Linux     ${{NC}}"
echo -e "${{BLUE}}===============================================${{NC}}"

# Determine target directories
if [ "$(id -u)" -eq 0 ]; then
    INSTALL_DIR="/usr/share/scarrar"
    BIN_DIR="/usr/local/bin"
    APPS_DIR="/usr/share/applications"
    ICONS_DIR="/usr/share/icons/hicolor/256x256/apps"
else
    echo -e "${{YELLOW}}[INFO] Running as regular user. Installing to ~/.local${{NC}}"
    INSTALL_DIR="$HOME/.local/share/scarrar"
    BIN_DIR="$HOME/.local/bin"
    APPS_DIR="$HOME/.local/share/applications"
    ICONS_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$APPS_DIR" "$ICONS_DIR"

SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"

echo "[1/4] Copying application files..."
cp "$SCRIPT_DIR/scarrar.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/scar_help.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/scarrar_favorites.json" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/scarrar.png" "$INSTALL_DIR/"
if [ -f "$SCRIPT_DIR/scarrar_icon.ico" ]; then
    cp "$SCRIPT_DIR/scarrar_icon.ico" "$INSTALL_DIR/"
fi

echo "[2/4] Installing runner script to $BIN_DIR/scarrar..."
cp "$SCRIPT_DIR/scarrar" "$BIN_DIR/scarrar"
chmod +x "$BIN_DIR/scarrar"

echo "[3/4] Installing desktop entry and high-res icon..."
cp "$SCRIPT_DIR/scarrar.desktop" "$APPS_DIR/"
cp "$SCRIPT_DIR/scarrar.png" "$ICONS_DIR/scarrar.png"

echo "[4/4] Updating system desktop and MIME databases..."
which update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" || true
which gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$(dirname $(dirname "$ICONS_DIR"))" || true

echo -e "${{GREEN}}SCAR RAR v{VERSION} successfully installed!${{NC}}"
echo -e "You can launch it from your application menu or run: ${{YELLOW}}scarrar${{NC}}"
"""

# D. Linux Uninstaller Script
linux_uninstall_sh = f"""#!/usr/bin/env bash
# ==============================================================================
# SCAR RAR Linux Uninstaller (v{VERSION})
# ==============================================================================
set -e

if [ "$(id -u)" -eq 0 ]; then
    rm -rf /usr/share/scarrar
    rm -f /usr/local/bin/scarrar
    rm -f /usr/share/applications/scarrar.desktop
    rm -f /usr/share/icons/hicolor/256x256/apps/scarrar.png
    which update-desktop-database >/dev/null 2>&1 && update-desktop-database /usr/share/applications || true
else
    rm -rf "$HOME/.local/share/scarrar"
    rm -f "$HOME/.local/bin/scarrar"
    rm -f "$HOME/.local/share/applications/scarrar.desktop"
    rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/scarrar.png"
    which update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" || true
fi

echo "SCAR RAR has been cleanly uninstalled from your Linux system."
"""

# Build Linux Portable Tarball
linux_tar_path = os.path.join(DIST_DIR, f"scarrar-v{VERSION}-linux.tar.gz")
with tarfile.open(linux_tar_path, "w:gz") as tar:
    def add_mem_file(arcname, text_or_bytes, mode=0o755):
        if isinstance(text_or_bytes, str):
            data = text_or_bytes.encode("utf-8")
        else:
            data = text_or_bytes
        ti = tarfile.TarInfo(name=arcname)
        ti.size = len(data)
        ti.mtime = int(time.time())
        ti.mode = mode
        tar.addfile(ti, io.BytesIO(data))

    folder_prefix = f"scarrar-v{VERSION}-linux"
    add_mem_file(f"{folder_prefix}/scarrar", linux_runner_content, 0o755)
    add_mem_file(f"{folder_prefix}/install.sh", linux_install_sh, 0o755)
    add_mem_file(f"{folder_prefix}/uninstall.sh", linux_uninstall_sh, 0o755)
    add_mem_file(f"{folder_prefix}/scarrar.desktop", desktop_content, 0o644)
    with open(icon_png_path, "rb") as f:
        add_mem_file(f"{folder_prefix}/scarrar.png", f.read(), 0o644)
    for sfn in src_files:
        sfp = os.path.join(ROOT_DIR, sfn)
        if os.path.exists(sfp):
            with open(sfp, "rb") as f:
                add_mem_file(f"{folder_prefix}/{sfn}", f.read(), 0o644)

print(f"Created Linux tarball: {linux_tar_path} ({os.path.getsize(linux_tar_path):,} bytes)")

# Build Debian / Ubuntu .deb Package
print("\n--- Building Debian .deb Package ---")
deb_pkg_path = os.path.join(DIST_DIR, f"scarrar_{VERSION}_all.deb")

# 1. debian-binary
deb_binary = b"2.0\n"

# 2. control.tar.gz
control_buf = io.BytesIO()
with tarfile.open(fileobj=control_buf, mode="w:gz") as tar:
    ctrl_txt = f"""Package: scarrar
Version: {VERSION}
Architecture: all
Maintainer: scar development <support@scarrar.com>
Installed-Size: 1500
Depends: python3, python3-tk, python3-pil, python3-pil.imagetk
Recommends: unrar | rar | p7zip-full
Section: utils
Priority: optional
Homepage: https://github.com/zakariamahdjoubi03-cloud/Scar-Rar
Description: SCAR RAR - High-Performance WinRAR Alternative
 Modern, ultra-fast archive manager with Dark Obsidian aesthetics.
 Supports RAR5, ZIP, ISO, 7Z, TAR, and CAB archive formats with maximum solid compression.
"""
    ti = tarfile.TarInfo(name="./control")
    ti.size = len(ctrl_txt.encode("utf-8"))
    ti.mode = 0o644
    ti.mtime = int(time.time())
    tar.addfile(ti, io.BytesIO(ctrl_txt.encode("utf-8")))

    postinst_txt = """#!/bin/sh
set -e
chmod +x /usr/bin/scarrar
which update-desktop-database >/dev/null 2>&1 && update-desktop-database -q /usr/share/applications || true
which gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q /usr/share/icons/hicolor || true
exit 0
"""
    ti_post = tarfile.TarInfo(name="./postinst")
    ti_post.size = len(postinst_txt.encode("utf-8"))
    ti_post.mode = 0o755
    ti_post.mtime = int(time.time())
    tar.addfile(ti_post, io.BytesIO(postinst_txt.encode("utf-8")))

control_data = control_buf.getvalue()

# 3. data.tar.gz
data_buf = io.BytesIO()
with tarfile.open(fileobj=data_buf, mode="w:gz") as tar:
    def add_data_file(arcname, content, mode=0o644):
        ti = tarfile.TarInfo(name=arcname)
        if isinstance(content, str):
            b = content.encode("utf-8")
        else:
            b = content
        ti.size = len(b)
        ti.mode = mode
        ti.mtime = int(time.time())
        tar.addfile(ti, io.BytesIO(b))

    add_data_file("./usr/bin/scarrar", linux_runner_content, 0o755)
    add_data_file("./usr/share/applications/scarrar.desktop", desktop_content, 0o644)
    with open(icon_png_path, "rb") as f:
        add_data_file("./usr/share/icons/hicolor/256x256/apps/scarrar.png", f.read(), 0o644)
    for sfn in src_files:
        sfp = os.path.join(ROOT_DIR, sfn)
        if os.path.exists(sfp):
            with open(sfp, "rb") as f:
                add_data_file(f"./usr/share/scarrar/{sfn}", f.read(), 0o644)

data_data = data_buf.getvalue()

# Write .deb (ar archive)
with open(deb_pkg_path, "wb") as f:
    f.write(b"!<arch>\n")
    for name, d, mode in [
        ("debian-binary", deb_binary, 0o100644),
        ("control.tar.gz", control_data, 0o100644),
        ("data.tar.gz", data_data, 0o100644)
    ]:
        hdr = bytearray()
        hdr.extend(f"{name:<16}".encode("ascii"))
        hdr.extend(f"{int(time.time()):<12}".encode("ascii"))
        hdr.extend(f"{0:<6}".encode("ascii"))
        hdr.extend(f"{0:<6}".encode("ascii"))
        hdr.extend(f"{oct(mode)[2:]:<8}".encode("ascii"))
        hdr.extend(f"{len(d):<10}".encode("ascii"))
        hdr.extend(b"\x60\n")
        f.write(hdr)
        f.write(d)
        if len(d) % 2 == 1:
            f.write(b"\n")

print(f"Created Debian .deb package: {deb_pkg_path} ({os.path.getsize(deb_pkg_path):,} bytes)")

# ==============================================================================
# MACOS BUILD (SCAR RAR.app + install.sh + ZIP)
# ==============================================================================
print("\n--- Building macOS Package ---")

macos_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>scarrar</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.scardevelopment.scarrar</string>
    <key>CFBundleName</key>
    <string>SCAR RAR</string>
    <key>CFBundleDisplayName</key>
    <string>SCAR RAR</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{VERSION}</string>
    <key>CFBundleVersion</key>
    <string>{VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Archive File</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>rar</string>
                <string>zip</string>
                <string>7z</string>
                <string>tar</string>
                <string>iso</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
"""

macos_runner = """#!/bin/bash
# SCAR RAR macOS Native App Launcher
DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Detect Python 3
PYTHON=""
for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3 $(which python3 2>/dev/null); do
    if [ -x "$candidate" ]; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    osascript -e 'display alert "Python 3 Required" message "SCAR RAR requires Python 3 with Tkinter. Please install Python 3 from brew or python.org."'
    exit 1
fi

export PYTHONPATH="$DIR/Resources:$PYTHONPATH"
exec "$PYTHON" "$DIR/Resources/scarrar.py" "$@"
"""

macos_install_sh = f"""#!/bin/bash
# ==============================================================================
# SCAR RAR macOS Installer (v{VERSION})
# ==============================================================================
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
APP_SRC="$DIR/SCAR RAR.app"
DEST_APP="/Applications/SCAR RAR.app"

echo "=== Installing SCAR RAR v{VERSION} on macOS ==="

if [ ! -d "$APP_SRC" ]; then
    echo "Error: SCAR RAR.app not found in $DIR"
    exit 1
fi

echo "Copying to /Applications..."
rm -rf "$DEST_APP"
cp -R "$APP_SRC" "$DEST_APP"

echo "Removing quarantine flags..."
xattr -dr com.apple.quarantine "$DEST_APP" 2>/dev/null || true

echo "Creating terminal shortcut: /usr/local/bin/scarrar..."
if [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    ln -sf "$DEST_APP/Contents/MacOS/scarrar" /usr/local/bin/scarrar
elif [ -d "$HOME/.local/bin" ]; then
    mkdir -p "$HOME/.local/bin"
    ln -sf "$DEST_APP/Contents/MacOS/scarrar" "$HOME/.local/bin/scarrar"
fi

echo "Registering application with macOS LaunchServices..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$DEST_APP" 2>/dev/null || true

echo "SUCCESS: SCAR RAR v{VERSION} is now installed in your /Applications folder!"
"""

macos_zip_path = os.path.join(DIST_DIR, f"SCAR-RAR-v{VERSION}-macOS.zip")
with zipfile.ZipFile(macos_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    def add_zip_str(arcname, content, executable=False):
        zi = zipfile.ZipInfo(arcname)
        zi.date_time = time.localtime(time.time())[:6]
        if executable:
            zi.external_attr = 0o755 << 16
        else:
            zi.external_attr = 0o644 << 16
        zf.writestr(zi, content)

    add_zip_str("SCAR RAR.app/Contents/Info.plist", macos_plist)
    add_zip_str("SCAR RAR.app/Contents/PkgInfo", "APPL????")
    add_zip_str("SCAR RAR.app/Contents/MacOS/scarrar", macos_runner, executable=True)
    with open(icns_path, "rb") as f:
        add_zip_str("SCAR RAR.app/Contents/Resources/AppIcon.icns", f.read())
    with open(icon_png_path, "rb") as f:
        add_zip_str("SCAR RAR.app/Contents/Resources/scarrar.png", f.read())
    for sfn in src_files:
        sfp = os.path.join(ROOT_DIR, sfn)
        if os.path.exists(sfp):
            with open(sfp, "rb") as f:
                add_zip_str(f"SCAR RAR.app/Contents/Resources/{sfn}", f.read())

    add_zip_str("install.sh", macos_install_sh, executable=True)
    add_zip_str("README-macOS.txt", f"""SCAR RAR v{VERSION} for macOS
================================

INSTALLATION:
1. Drag 'SCAR RAR.app' into your /Applications folder, OR
2. Double-click or run:
   ./install.sh

REQUIREMENTS:
- macOS 10.13 or newer (Supports Intel and Apple Silicon M1/M2/M3/M4)
- Python 3 with Tkinter (Installed by default or via: brew install python-tk)

CLI USAGE:
You can use SCAR RAR from terminal:
  scarrar /path/to/archive.rar
  scarrar -a file1 file2
  scarrar -x archive.rar
""")

print(f"Created macOS zip bundle: {macos_zip_path} ({os.path.getsize(macos_zip_path):,} bytes)")

print("\nALL LINUX & MACOS PACKAGES GENERATED SUCCESSFULLY!")
