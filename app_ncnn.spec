
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_ncnn.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bin/*', 'bin'),
        ('models/*', 'models'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PIL._tkinter_finder',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'numpy',
        'qdarkstyle',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RealESRGAN-NCNN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RealESRGAN-NCNN',
)
