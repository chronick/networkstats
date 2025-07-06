# App Packaging and Deployment Specification: Current Implementation



## PyInstaller Configuration

# NetworkStats.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('networkstats', 'networkstats'),
    ],
    hiddenimports=['rumps', 'toga', 'plotly', 'polars'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NetworkStats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='NetworkStats.app',
    icon='assets/NetworkStats.icns',
    bundle_identifier='com.networkstats.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # Hide from dock
        'NSRequiresAquaSystemAppearance': False,  # Dark mode support
    },
)

```python
# NetworkStats.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('networkstats', 'networkstats'),
    ],
    hiddenimports=['rumps', 'toga', 'plotly', 'polars'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NetworkStats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='NetworkStats.app',
    icon='assets/NetworkStats.icns',
    bundle_identifier='com.networkstats.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # Hide from dock
        'NSRequiresAquaSystemAppearance': False,  # Dark mode support
    },
)

```
