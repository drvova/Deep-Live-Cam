# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('/home/drvova/PersonaMesh/Deep-Live-Cam/modules/ui/theme.json', 'modules/ui'), ('/home/drvova/PersonaMesh/Deep-Live-Cam/locales', 'locales'), ('/home/drvova/PersonaMesh/Deep-Live-Cam/media', 'media'), ('/home/drvova/PersonaMesh/Deep-Live-Cam/tkinter_fix.py', '.')]
binaries = []
hiddenimports = ['modules', 'modules.core', 'modules.core.app', 'modules.core.types', 'modules.config', 'modules.config.globals', 'modules.config.metadata', 'modules.face', 'modules.face.analyser', 'modules.face.cluster', 'modules.face.predicter', 'modules.media', 'modules.media.ffmpeg', 'modules.media.capturer', 'modules.media.video_capture', 'modules.processors', 'modules.processors.registry', 'modules.processors.frame', 'modules.processors.frame.swapper', 'modules.processors.frame.enhancer', 'modules.processors.frame.masking', 'modules.ui', 'modules.ui.app', 'modules.ui.fix', 'modules.i18n', 'modules.i18n.manager', 'cv2', 'numpy', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'customtkinter', 'tkinter', 'tkinter.filedialog', 'tkinter.messagebox', 'onnxruntime', 'onnxruntime.capi', 'insightface', 'insightface.app', 'insightface.model_zoo', 'torch', 'torchvision', 'psutil', 'pygrabber', 'cv2_enumerate_cameras', 'jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.context', 'platformdirs', 'pkg_resources', 'setuptools', 'setuptools._vendor', 'setuptools._vendor.jaraco', 'setuptools._vendor.jaraco.text', 'setuptools._vendor.platformdirs']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('onnxruntime')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jaraco')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('platformdirs')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['/home/drvova/PersonaMesh/Deep-Live-Cam/run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'IPython', 'jupyter', 'notebook', 'pytest', 'sphinx', 'wheel'],
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
    console=False,
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
    upx_exclude=[],
    name='Deep-Live-Cam',
)
