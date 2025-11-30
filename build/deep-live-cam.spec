# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Deep-Live-Cam Windows build.
Cross-platform compatible - works on Windows native or via Wine.

Usage:
    pyinstaller deep-live-cam.spec

For one-file build:
    pyinstaller deep-live-cam.spec --onefile
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Project root directory (one level up from build/)
PROJECT_ROOT = Path(SPECPATH).parent.resolve()

# Collect data files
datas = [
    # UI theme configuration
    (str(PROJECT_ROOT / 'modules' / 'ui' / 'theme.json'), 'modules/ui'),

    # Localization files
    (str(PROJECT_ROOT / 'locales'), 'locales'),

    # Models directory (if models are bundled)
    # (str(PROJECT_ROOT / 'models'), 'models'),

    # Media assets
    (str(PROJECT_ROOT / 'media'), 'media'),

    # tkinter fix module
    (str(PROJECT_ROOT / 'tkinter_fix.py'), '.'),
]

# Hidden imports for dynamic loading
hiddenimports = [
    # Core modules
    'modules',
    'modules.core',
    'modules.core.app',
    'modules.core.types',
    'modules.config',
    'modules.config.globals',
    'modules.config.metadata',

    # Face processing
    'modules.face',
    'modules.face.analyser',
    'modules.face.cluster',
    'modules.face.predicter',

    # Media handling
    'modules.media',
    'modules.media.ffmpeg',
    'modules.media.capturer',
    'modules.media.video_capture',

    # Processors
    'modules.processors',
    'modules.processors.registry',
    'modules.processors.frame',
    'modules.processors.frame.swapper',
    'modules.processors.frame.enhancer',
    'modules.processors.frame.masking',

    # UI
    'modules.ui',
    'modules.ui.app',
    'modules.ui.fix',

    # i18n
    'modules.i18n',
    'modules.i18n.manager',

    # Third-party dependencies
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'customtkinter',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',

    # ONNX Runtime providers
    'onnxruntime',
    'onnxruntime.capi',
    'onnxruntime.capi._pybind_state',

    # InsightFace
    'insightface',
    'insightface.app',
    'insightface.model_zoo',
    'insightface.utils',

    # Torch (optional GPU support)
    'torch',
    'torchvision',

    # TensorFlow (for GFPGAN)
    'tensorflow',

    # Additional dependencies
    'psutil',
    'pygrabber',
    'cv2_enumerate_cameras',
]

# Binary files to include
binaries = []

# Exclude unnecessary modules to reduce size
excludes = [
    'matplotlib',
    'pandas',
    'scipy.spatial.cKDTree',  # Not needed
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'sphinx',
]

a = Analysis(
    [str(PROJECT_ROOT / 'run.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out unnecessary files to reduce bundle size
def filter_binaries(binaries_list):
    """Remove duplicate and unnecessary binaries."""
    seen = set()
    filtered = []
    for item in binaries_list:
        name = item[0]
        if name not in seen:
            seen.add(name)
            # Skip test files and documentation
            if not any(x in name.lower() for x in ['test', 'tests', 'doc', 'docs', 'example']):
                filtered.append(item)
    return filtered

a.binaries = filter_binaries(a.binaries)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Main executable
exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty for one-dir mode; a.binaries for one-file
    exclude_binaries=True,  # Set to False for one-file mode
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
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / 'media' / 'icon.ico') if (PROJECT_ROOT / 'media' / 'icon.ico').exists() else None,
    version_file=None,
)

# Collect all files into distribution folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
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
