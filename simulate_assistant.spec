# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/visionnav/workspace/simulaite_assistant-5.2.0.13-forshadow_be_startup/scripts/VN_WebotsLauncherX.py'],
    pathex=[],
    binaries=[('/home/visionnav/workspace/simulaite_assistant-5.2.0.13-forshadow_be_startup/scripts/VN_WebotsLauncherX.py', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='simulate_assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
