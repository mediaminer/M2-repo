# -*- mode: python ; coding: utf-8 -*-
import os

# Define the path to your icon file
icon_path = "M2.icns"

# Explicitly define Whisper assets needed (instead of collect_all)
whisper_assets = [
    ('/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/whisper/assets/mel_filters.npz', 'whisper/assets'),
    ('/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/whisper/assets/multilingual.tiktoken', 'whisper/assets')
]

# Create the datas list (make sure it's in the correct tuple format)
datas = whisper_assets + [(icon_path, '.')]

a = Analysis(
    ['M2.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='M2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='M2'
)

# ✒️ Signature
# (M2000 - M2 1.0)
