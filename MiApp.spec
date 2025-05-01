# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['App\\main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('App/icons', 'App/icons'), ('config/config.yaml', 'config')],
    hiddenimports=['Analizer.acoustic_index', 'Analizer.Analizer', 'Analizer.compute_indice', 'Analizer.progress', 'Analizer.tester'],
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
    name='MiApp',
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
