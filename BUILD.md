# Deep-Live-Cam Build Guide

Comprehensive guide for building Deep-Live-Cam executables for Windows, Linux, and macOS.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Windows Build](#windows-build)
  - [Native Windows Build](#native-windows-build)
  - [Cross-Compile from Linux](#cross-compile-from-linux)
- [Linux Build](#linux-build)
- [macOS Build](#macos-build)
- [GitHub Actions (Recommended)](#github-actions-recommended)
- [Creating Installers](#creating-installers)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### All Platforms

- **Python 3.10+** (3.10 or 3.11 recommended)
- **pip** (latest version)
- **Git** (for cloning dependencies)

### Build Tools

```bash
# Install PyInstaller
pip install pyinstaller>=6.0.0

# Optional: UPX for compression (reduces executable size by ~50%)
# Windows: Download from https://github.com/upx/upx/releases
# Linux: sudo apt install upx
# macOS: brew install upx
```

### Project Dependencies

```bash
# Clone the repository
git clone https://github.com/hacksider/Deep-Live-Cam.git
cd Deep-Live-Cam

# Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

### Using the Build Script (Recommended)

```bash
# Build for current platform (directory mode - easier to debug)
python build/build.py

# Build single executable
python build/build.py --mode onefile

# Build with console output (for debugging)
python build/build.py --debug

# Clean build artifacts
python build/build.py --clean
```

### Manual PyInstaller Command

```bash
pyinstaller --clean --noconfirm \
    --name=Deep-Live-Cam \
    --windowed \
    --add-data="modules/ui/theme.json:modules/ui" \
    --add-data="locales:locales" \
    --add-data="media:media" \
    --hidden-import=modules.core.app \
    --hidden-import=customtkinter \
    --hidden-import=onnxruntime \
    --collect-all=customtkinter \
    run.py
```

---

## Windows Build

### Native Windows Build

**Option 1: Using the Batch Script**

```cmd
cd Deep-Live-Cam

REM Standard build (directory mode)
build\build-windows.bat

REM Single executable
build\build-windows.bat onefile

REM Debug build (with console)
build\build-windows.bat debug

REM Clean
build\build-windows.bat clean
```

**Option 2: Using Python Build Script**

```cmd
python build\build.py --mode onedir
```

**Option 3: Manual PyInstaller**

```cmd
pyinstaller --clean --noconfirm ^
    --name=Deep-Live-Cam ^
    --windowed ^
    --icon=media\icon.ico ^
    --add-data="modules\ui\theme.json;modules\ui" ^
    --add-data="locales;locales" ^
    --add-data="media;media" ^
    --add-data="tkinter_fix.py;." ^
    --hidden-import=modules.core.app ^
    --hidden-import=modules.config.globals ^
    --hidden-import=modules.face.analyser ^
    --hidden-import=modules.processors.frame.swapper ^
    --hidden-import=customtkinter ^
    --hidden-import=onnxruntime ^
    --hidden-import=insightface ^
    --collect-all=customtkinter ^
    --collect-all=onnxruntime ^
    run.py
```

**Output:** `dist\Deep-Live-Cam\Deep-Live-Cam.exe`

### Cross-Compile from Linux

> ⚠️ **Note:** True cross-compilation is complex. We recommend using GitHub Actions instead.

**Using Docker + Wine:**

```bash
# Build the Docker image
docker build -t deep-live-cam-builder -f build/Dockerfile.windows .

# Run the build
docker run --rm \
    -v $(pwd):/src \
    -v $(pwd)/dist:/dist \
    deep-live-cam-builder
```

**Limitations:**
- Some native Windows libraries may not work correctly under Wine
- GPU support (CUDA/DirectML) requires native Windows testing
- Recommended: Use GitHub Actions for production Windows builds

---

## Linux Build

### Native Linux Build

```bash
# Standard build
python build/build.py --mode onedir

# Single executable (larger file, slower startup)
python build/build.py --mode onefile

# With debug console
python build/build.py --debug
```

### Manual Build

```bash
pyinstaller --clean --noconfirm \
    --name=Deep-Live-Cam \
    --windowed \
    --add-data="modules/ui/theme.json:modules/ui" \
    --add-data="locales:locales" \
    --add-data="media:media" \
    --add-data="tkinter_fix.py:." \
    --hidden-import=modules.core.app \
    --hidden-import=customtkinter \
    --hidden-import=onnxruntime \
    --collect-all=customtkinter \
    run.py
```

**Output:** `dist/Deep-Live-Cam/Deep-Live-Cam`

### Creating a Tarball

```bash
cd dist
tar -czvf Deep-Live-Cam-Linux-x86_64.tar.gz Deep-Live-Cam/
```

### Creating an AppImage

```bash
# Install appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p Deep-Live-Cam.AppDir/usr/bin
cp -r dist/Deep-Live-Cam/* Deep-Live-Cam.AppDir/usr/bin/

# Create desktop entry
cat > Deep-Live-Cam.AppDir/Deep-Live-Cam.desktop << EOF
[Desktop Entry]
Type=Application
Name=Deep-Live-Cam
Exec=Deep-Live-Cam
Icon=deep-live-cam
Categories=Graphics;Video;
EOF

# Create AppRun
cat > Deep-Live-Cam.AppDir/AppRun << EOF
#!/bin/bash
cd "\$(dirname "\$0")/usr/bin"
exec ./Deep-Live-Cam "\$@"
EOF
chmod +x Deep-Live-Cam.AppDir/AppRun

# Build AppImage
./appimagetool-x86_64.AppImage Deep-Live-Cam.AppDir Deep-Live-Cam-x86_64.AppImage
```

---

## macOS Build

### Native macOS Build

```bash
# Standard build (universal binary for Intel + Apple Silicon)
python build/build.py --mode onedir

# Single executable
python build/build.py --mode onefile
```

### Manual Build

```bash
pyinstaller --clean --noconfirm \
    --name=Deep-Live-Cam \
    --windowed \
    --icon=media/icon.icns \
    --target-arch=universal2 \
    --add-data="modules/ui/theme.json:modules/ui" \
    --add-data="locales:locales" \
    --add-data="media:media" \
    --add-data="tkinter_fix.py:." \
    --hidden-import=modules.core.app \
    --hidden-import=customtkinter \
    --hidden-import=onnxruntime \
    --collect-all=customtkinter \
    run.py
```

**Output:** `dist/Deep-Live-Cam.app`

### Creating a DMG

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
    --volname "Deep-Live-Cam" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --app-drop-link 450 185 \
    "Deep-Live-Cam-macOS.dmg" \
    "dist/Deep-Live-Cam.app"
```

### Code Signing (Optional)

```bash
# Sign the app
codesign --force --deep --sign "Developer ID Application: Your Name" dist/Deep-Live-Cam.app

# Notarize (requires Apple Developer account)
xcrun notarytool submit Deep-Live-Cam-macOS.dmg \
    --apple-id "your@email.com" \
    --password "app-specific-password" \
    --team-id "TEAMID"
```

---

## GitHub Actions (Recommended)

The easiest way to build for all platforms is using GitHub Actions.

### Generate Workflow

```bash
python build/build.py --github-workflow
```

This creates `.github/workflows/build-release.yml` which:
- Builds for Windows, Linux, and macOS
- Uploads artifacts for each platform
- Creates releases when you push a version tag

### Trigger a Build

```bash
# Manual trigger via GitHub UI
# Or push a version tag:
git tag v1.0.0
git push origin v1.0.0
```

---

## Creating Installers

### Windows Installer (Inno Setup)

1. **Generate the Inno Setup script:**

```bash
python build/build.py --inno-setup
```

2. **Download Inno Setup:** https://jrsoftware.org/isinfo.php

3. **Compile the installer:**

```cmd
iscc build\installer.iss
```

**Output:** `dist\Deep-Live-Cam-Setup-1.0.0.exe`

### Windows MSIX (Microsoft Store)

For Microsoft Store distribution, consider using the MSIX Packaging Tool or converting with makeappx.

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'xxx'"

Add the missing module as a hidden import:

```bash
pyinstaller ... --hidden-import=missing_module
```

Or update `BuildConfig.HIDDEN_IMPORTS` in `build/build.py`.

#### 2. CustomTkinter themes not loading

Ensure the theme file is bundled:

```bash
--add-data="modules/ui/theme.json:modules/ui"
```

And use `--collect-all=customtkinter` to include all CustomTkinter assets.

#### 3. ONNX Runtime errors

```bash
--collect-all=onnxruntime
--hidden-import=onnxruntime.capi._pybind_state
```

#### 4. InsightFace model loading fails

Models are loaded from `~/.insightface/models/` at runtime. They are NOT bundled with the executable. Users need to:
1. Run the app once to download models automatically
2. Or manually download and place models in the correct directory

#### 5. Large executable size

- Use UPX compression: Remove `--noupx` flag
- Exclude unnecessary modules:
  ```bash
  --exclude-module=matplotlib
  --exclude-module=pandas
  --exclude-module=scipy
  ```

#### 6. Slow startup (onefile mode)

The `--onefile` mode extracts to a temp directory on each run. Use `--onedir` for faster startup.

#### 7. Windows Defender false positive

Some antivirus software flags PyInstaller executables. Solutions:
- Sign the executable with a code signing certificate
- Submit for whitelisting to antivirus vendors
- Use `--key` option to encrypt Python bytecode

### Debug Mode

Build with console output to see error messages:

```bash
python build/build.py --debug
# or
pyinstaller ... --console
```

### Verbose PyInstaller Output

```bash
pyinstaller --log-level=DEBUG ...
```

---

## Build Modes Comparison

| Feature | `--onedir` | `--onefile` |
|---------|-----------|-------------|
| Startup Speed | Fast | Slow (extracts on each run) |
| File Size | Larger (many files) | Smaller (single file) |
| Distribution | Zip/Folder | Single .exe |
| Updates | Easy (replace files) | Must replace entire exe |
| Antivirus Issues | Fewer | More common |
| Debugging | Easier | Harder |

**Recommendation:** Use `--onedir` for development and testing, `--onefile` for simple distribution.

---

## Directory Structure After Build

```
dist/
└── Deep-Live-Cam/
    ├── Deep-Live-Cam.exe          # Main executable
    ├── _internal/                  # Python runtime and dependencies
    │   ├── customtkinter/
    │   ├── onnxruntime/
    │   ├── cv2/
    │   └── ...
    ├── locales/                    # Localization files
    ├── media/                      # Media assets
    └── modules/
        └── ui/
            └── theme.json          # UI theme configuration
```

---

## External Dependencies

The executable requires these external tools to be available on the user's system:

- **FFmpeg** - For video processing (must be in PATH or specify location)
- **CUDA Toolkit** (optional) - For NVIDIA GPU acceleration
- **DirectML** (optional) - For AMD/Intel GPU acceleration on Windows

---

## Version Information

To embed version information in the Windows executable, create a version file:

```python
# build/version_info.py
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
    ),
    kids=[
        StringFileInfo([
            StringTable('040904B0', [
                StringStruct('CompanyName', 'Deep-Live-Cam Team'),
                StringStruct('ProductName', 'Deep-Live-Cam'),
                StringStruct('ProductVersion', '1.0.0'),
            ])
        ])
    ]
)
```

Then add to PyInstaller:
```bash
pyinstaller ... --version-file=build/version_info.py
```

---

## Support

If you encounter build issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on GitHub with:
   - Your operating system and version
   - Python version (`python --version`)
   - PyInstaller version (`pyinstaller --version`)
   - Complete error message/traceback
   - Build command used