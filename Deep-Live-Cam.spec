# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Deep-Live-Cam.
Console is enabled for debugging - set console=False for production builds.
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collect all customtkinter assets
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

# Collect all onnxruntime assets
onnx_datas, onnx_binaries, onnx_hiddenimports = collect_all('onnxruntime')

datas = [
    ('modules/ui/theme.json', 'modules/ui'),
    ('locales', 'locales'),
    ('media', 'media'),
    ('tkinter_fix.py', '.'),
]
datas += ctk_datas
datas += onnx_datas

binaries = []
binaries += ctk_binaries
binaries += onnx_binaries

hiddenimports = [
    # Core modules
    'modules',
    'modules.core',
    'modules.core.app',
    'modules.core.types',
    'modules.config',
    'modules.config.globals',
    'modules.config.metadata',
    'modules.face',
    'modules.face.analyser',
    'modules.face.cluster',
    'modules.face.predicter',
    'modules.media',
    'modules.media.ffmpeg',
    'modules.media.capturer',
    'modules.media.video_capture',
    'modules.processors',
    'modules.processors.registry',
    'modules.processors.frame',
    'modules.processors.frame.swapper',
    'modules.processors.frame.enhancer',
    'modules.processors.frame.masking',
    'modules.ui',
    'modules.ui.app',
    'modules.ui.fix',
    'modules.i18n',
    'modules.i18n.manager',
    # Third-party
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'customtkinter',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'onnxruntime',
    'onnxruntime.capi',
    'onnxruntime.capi._pybind_state',
    'insightface',
    'insightface.app',
    'insightface.model_zoo',
    'insightface.utils',
    'tensorflow',
    'torch',
    'torchvision',
    'psutil',
    'pygrabber',
    'pygrabber.dshow_graph',
    'cv2_enumerate_cameras',
    # Jaraco packages
    'jaraco',
    'jaraco.text',
    'jaraco.functools',
    'jaraco.context',
    # pkg_resources
    'platformdirs',
    'pkg_resources',
    'setuptools',
]
hiddenimports += ctk_hiddenimports
hiddenimports += onnx_hiddenimports

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Deep-Live-Cam',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python*.dll',
        'onnxruntime*.dll',
    ],
    console=True,  # ENABLED for debugging - set to False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python*.dll',
        'onnxruntime*.dll',
    ],
    name='Deep-Live-Cam',
)
