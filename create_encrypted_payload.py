# -*- coding: utf-8 -*-
import os
import io
import sys
import zipfile
import hashlib
import shutil

def create_payload():
    dist_dir = os.path.join(os.getcwd(), "dist", "SCAR RAR")
    assert os.path.isdir(dist_dir), f"Dist dir not found: {dist_dir}"

    # Ensure auxiliary files exist in dist_dir
    aux_files = ["Rar.exe", "UnRAR.exe", "scarrar_icon.ico", "scarrar_favorites.json", "uninstall.exe"]
    for f in aux_files:
        src = os.path.join(os.getcwd(), f)
        dst = os.path.join(dist_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Copied {f} into dist folder")

    # Also copy UnRAR.exe and Rar.exe into _internal for 100% path safety in PyInstaller one-dir mode
    internal_dir = os.path.join(dist_dir, "_internal")
    if os.path.isdir(internal_dir):
        for f in ["Rar.exe", "UnRAR.exe"]:
            src = os.path.join(os.getcwd(), f)
            dst = os.path.join(internal_dir, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Copied {f} into _internal folder")

    # Pack entire dist_dir into a zip byte buffer
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dist_dir)
                zf.write(full_path, rel_path)

    raw_zip_bytes = zip_buf.getvalue()
    raw_size = len(raw_zip_bytes)
    print(f"Raw ZIP payload size: {raw_size:,} bytes")

    # Compute checksum
    raw_checksum = hashlib.sha256(raw_zip_bytes).digest()

    # Encryption key stream
    key_mat = b"scar-development-scarrar-secure-protection-key-2026-v1.0"
    derived_k = hashlib.sha256(key_mat).digest()
    k_len = len(derived_k)

    enc_data = bytearray(raw_zip_bytes)
    for i in range(len(enc_data)):
        enc_data[i] ^= derived_k[i % k_len]

    magic = b"SCAR_RAR_ENCRYPTED_PAYLOAD_V1\x00"

    out_file = os.path.join(os.getcwd(), "scar_payload.enc")
    with open(out_file, "wb") as fout:
        fout.write(magic)
        fout.write(raw_checksum)
        fout.write(enc_data)

    enc_size = os.path.getsize(out_file)
    print(f"Encrypted payload written to {out_file} ({enc_size:,} bytes)")
    print("SUCCESS: Payload encrypted with scar development proprietary keystream.")

if __name__ == "__main__":
    create_payload()
