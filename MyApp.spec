# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('index.html', '.'), ('core.py', '.'), ('bridge.js', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['cryptography','fastapi', 'uvicorn','starlette', 'pydantic', 'anyio', 'httptools','click', 'h11', 'websockets', 'wsproto'],
    noarchive=False,
    optimize=0,
)

# 关键：过滤掉 OpenSSL 相关的 DLL
a.binaries = [x for x in a.binaries if not any(dll in x[0].lower() for dll in [
    'libcrypto'
])]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['libcrypto-3-x64.dll'],  # 可选：UPX 也不压缩
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
