#!/usr/bin/env python3
"""
Deep-Live-Cam Build Script
==========================

Comprehensive build system for creating distributable packages across platforms.

Supported platforms:
    - Windows (native or cross-compile via Wine)
    - Linux (native)
    - macOS (native)

Usage:
    python build.py --platform windows --mode onedir
    python build.py --platform linux --mode onefile
    python build.py --clean
    python build.py --help

Requirements:
    - PyInstaller >= 6.0.0
    - UPX (optional, for compression)
    - Wine (for Windows cross-compilation on Linux)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class BuildConfig:
    """Build configuration container."""

    PROJECT_NAME = "Deep-Live-Cam"
    VERSION = "1.0.0"

    # Directories
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    BUILD_DIR = PROJECT_ROOT / "build"
    DIST_DIR = PROJECT_ROOT / "dist"
    SPEC_FILE = BUILD_DIR / "deep-live-cam.spec"

    # Entry point
    ENTRY_SCRIPT = PROJECT_ROOT / "run.py"

    # Icon paths
    ICON_WINDOWS = PROJECT_ROOT / "media" / "icon.ico"
    ICON_MACOS = PROJECT_ROOT / "media" / "icon.icns"
    ICON_LINUX = PROJECT_ROOT / "media" / "icon.png"

    # Data files to bundle
    DATA_FILES = [
        ("modules/ui/theme.json", "modules/ui"),
        ("locales", "locales"),
        ("media", "media"),
        ("tkinter_fix.py", "."),
    ]

    # Hidden imports for dynamic module loading
    HIDDEN_IMPORTS = [
        # Core modules
        "modules",
        "modules.core",
        "modules.core.app",
        "modules.core.types",
        "modules.config",
        "modules.config.globals",
        "modules.config.metadata",
        "modules.face",
        "modules.face.analyser",
        "modules.face.cluster",
        "modules.face.predicter",
        "modules.media",
        "modules.media.ffmpeg",
        "modules.media.capturer",
        "modules.media.video_capture",
        "modules.processors",
        "modules.processors.registry",
        "modules.processors.frame",
        "modules.processors.frame.swapper",
        "modules.processors.frame.enhancer",
        "modules.processors.frame.masking",
        "modules.ui",
        "modules.ui.app",
        "modules.ui.fix",
        "modules.i18n",
        "modules.i18n.manager",
        # Third-party
        "cv2",
        "numpy",
        "PIL",
        "PIL.Image",
        "PIL.ImageTk",
        "customtkinter",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "onnxruntime",
        "onnxruntime.capi",
        "insightface",
        "insightface.app",
        "insightface.model_zoo",
        "torch",
        "torchvision",
        "psutil",
        "pygrabber",
        "cv2_enumerate_cameras",
        # Jaraco packages (required by pkg_resources)
        "jaraco",
        "jaraco.text",
        "jaraco.functools",
        "jaraco.context",
        # Additional pkg_resources dependencies
        "platformdirs",
        "pkg_resources",
        "setuptools",
        "setuptools._vendor",
        "setuptools._vendor.jaraco",
        "setuptools._vendor.jaraco.text",
        "setuptools._vendor.platformdirs",
    ]

    # Collect-all packages (bundle all submodules and data)
    COLLECT_ALL = [
        "customtkinter",
        "onnxruntime",
        "jaraco",
        "platformdirs",
    ]

    # Modules to exclude
    EXCLUDES = [
        "matplotlib",
        "pandas",
        "IPython",
        "jupyter",
        "notebook",
        "pytest",
        "sphinx",
        "wheel",
    ]


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def log(msg: str, color: str = "") -> None:
    """Print colored log message."""
    print(f"{color}{msg}{Colors.RESET}")


def log_info(msg: str) -> None:
    log(f"[INFO] {msg}", Colors.CYAN)


def log_success(msg: str) -> None:
    log(f"[SUCCESS] {msg}", Colors.GREEN)


def log_warning(msg: str) -> None:
    log(f"[WARNING] {msg}", Colors.YELLOW)


def log_error(msg: str) -> None:
    log(f"[ERROR] {msg}", Colors.RED)


def log_header(msg: str) -> None:
    log(f"\n{'=' * 60}\n{msg}\n{'=' * 60}", Colors.BOLD + Colors.HEADER)


def run_command(
    cmd: list, cwd: Optional[Path] = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Execute a command and return the result."""
    log_info(f"Running: {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=cwd or BuildConfig.PROJECT_ROOT,
        check=check,
        capture_output=False,
    )


def check_dependencies() -> bool:
    """Verify all build dependencies are installed."""
    log_header("Checking Dependencies")

    missing = []

    # Check Python version
    if sys.version_info < (3, 10):
        log_error(f"Python 3.10+ required, found {sys.version}")
        return False
    log_success(f"Python {sys.version_info.major}.{sys.version_info.minor} OK")

    # Check PyInstaller
    try:
        import PyInstaller

        log_success(f"PyInstaller {PyInstaller.__version__} OK")
    except ImportError:
        missing.append("pyinstaller")
        log_warning("PyInstaller not found")

    # Check UPX (optional)
    upx_path = shutil.which("upx")
    if upx_path:
        log_success(f"UPX found at {upx_path}")
    else:
        log_warning("UPX not found (optional, for compression)")

    # Install missing dependencies
    if missing:
        log_info(f"Installing missing dependencies: {missing}")
        run_command([sys.executable, "-m", "pip", "install"] + missing)

    return True


def clean_build_artifacts() -> None:
    """Remove all build artifacts."""
    log_header("Cleaning Build Artifacts")

    dirs_to_clean = [
        BuildConfig.DIST_DIR,
        BuildConfig.BUILD_DIR / "dist",
        BuildConfig.BUILD_DIR / "build",
        BuildConfig.PROJECT_ROOT / "__pycache__",
    ]

    # Also clean .spec files in project root
    for spec in BuildConfig.PROJECT_ROOT.glob("*.spec"):
        if spec != BuildConfig.SPEC_FILE:
            log_info(f"Removing {spec}")
            spec.unlink()

    for d in dirs_to_clean:
        if d.exists():
            log_info(f"Removing {d}")
            shutil.rmtree(d, ignore_errors=True)

    log_success("Clean complete")


def get_platform_icon() -> Optional[str]:
    """Get the appropriate icon path for the current platform."""
    system = platform.system().lower()

    if system == "windows":
        icon = BuildConfig.ICON_WINDOWS
    elif system == "darwin":
        icon = BuildConfig.ICON_MACOS
    else:
        icon = BuildConfig.ICON_LINUX

    return str(icon) if icon.exists() else None


def build_pyinstaller_args(
    target_platform: str,
    mode: str,
    debug: bool = False,
    upx: bool = True,
) -> list:
    """Construct PyInstaller command arguments."""

    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        f"--name={BuildConfig.PROJECT_NAME}",
        f"--distpath={BuildConfig.DIST_DIR}",
        f"--workpath={BuildConfig.BUILD_DIR / 'work'}",
        f"--specpath={BuildConfig.BUILD_DIR}",
    ]

    # Build mode
    if mode == "onefile":
        args.append("--onefile")
    else:
        args.append("--onedir")

    # Console/windowed mode
    if debug:
        args.append("--console")
    else:
        args.append("--windowed")

    # UPX compression
    if not upx:
        args.append("--noupx")

    # Icon
    icon = get_platform_icon()
    if icon:
        args.append(f"--icon={icon}")

    # Data files
    separator = ";" if target_platform == "windows" else ":"
    for src, dst in BuildConfig.DATA_FILES:
        src_path = BuildConfig.PROJECT_ROOT / src
        if src_path.exists():
            args.append(f"--add-data={src_path}{separator}{dst}")

    # Hidden imports
    for imp in BuildConfig.HIDDEN_IMPORTS:
        args.append(f"--hidden-import={imp}")

    # Excludes
    for exc in BuildConfig.EXCLUDES:
        args.append(f"--exclude-module={exc}")

    # Collect-all packages
    for pkg in BuildConfig.COLLECT_ALL:
        args.append(f"--collect-all={pkg}")

    # Platform-specific options
    if target_platform == "windows":
        pass  # collect-all already added above
    elif target_platform == "darwin":
        args.append("--target-arch=universal2")

    # Entry script
    args.append(str(BuildConfig.ENTRY_SCRIPT))

    return args


def build_native(
    mode: str = "onedir",
    debug: bool = False,
    upx: bool = True,
) -> bool:
    """Build for the current platform."""
    system = platform.system().lower()
    target = (
        "windows"
        if system == "windows"
        else ("darwin" if system == "darwin" else "linux")
    )

    log_header(f"Building for {target.upper()} ({mode} mode)")

    args = build_pyinstaller_args(target, mode, debug, upx)

    try:
        run_command(args)
        log_success(f"Build complete! Output: {BuildConfig.DIST_DIR}")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Build failed: {e}")
        return False


def build_windows_cross() -> bool:
    """Cross-compile for Windows using Wine (Linux only)."""
    log_header("Cross-compiling for Windows via Wine")

    if platform.system() != "Linux":
        log_error("Windows cross-compilation only supported on Linux")
        return False

    # Check Wine
    if not shutil.which("wine"):
        log_error("Wine not found. Install with: sudo apt install wine64 wine32")
        return False

    log_warning("Cross-compilation via Wine is experimental.")
    log_info("For best results, use a Windows machine or GitHub Actions.")

    # Use Docker if available
    if shutil.which("docker"):
        log_info("Docker found. Using containerized build...")
        dockerfile = BuildConfig.BUILD_DIR / "Dockerfile.windows"

        if not dockerfile.exists():
            log_error(f"Dockerfile not found: {dockerfile}")
            return False

        try:
            # Build Docker image
            run_command(
                [
                    "docker",
                    "build",
                    "-t",
                    "deep-live-cam-builder",
                    "-f",
                    str(dockerfile),
                    str(BuildConfig.PROJECT_ROOT),
                ]
            )

            # Run build in container
            run_command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{BuildConfig.PROJECT_ROOT}:/src",
                    "-v",
                    f"{BuildConfig.DIST_DIR}:/dist",
                    "deep-live-cam-builder",
                ]
            )

            log_success("Docker build complete!")
            return True

        except subprocess.CalledProcessError as e:
            log_error(f"Docker build failed: {e}")
            return False

    log_error("Docker not found. Cannot proceed with cross-compilation.")
    log_info("Alternative: Use GitHub Actions for Windows builds.")
    return False


def create_github_workflow() -> None:
    """Generate GitHub Actions workflow for multi-platform builds."""
    log_header("Creating GitHub Actions Workflow")

    workflow_dir = BuildConfig.PROJECT_ROOT / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    workflow_file = workflow_dir / "build-release.yml"

    workflow_content = """name: Build Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest
            artifact: Deep-Live-Cam-Windows

          - os: ubuntu-22.04
            artifact: Deep-Live-Cam-Linux

          - os: macos-latest
            artifact: Deep-Live-Cam-macOS

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: python build/build.py --mode onedir

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact }}
          path: dist/
          retention-days: 30

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')

    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            Deep-Live-Cam-Windows/**
            Deep-Live-Cam-Linux/**
            Deep-Live-Cam-macOS/**
          generate_release_notes: true
"""

    workflow_file.write_text(workflow_content)
    log_success(f"Created {workflow_file}")


def create_inno_setup_script() -> None:
    """Generate Inno Setup script for Windows installer."""
    log_header("Creating Inno Setup Script")

    iss_file = BuildConfig.BUILD_DIR / "installer.iss"

    iss_content = f'''; Inno Setup Script for Deep-Live-Cam
; Generates professional Windows installer

#define MyAppName "{BuildConfig.PROJECT_NAME}"
#define MyAppVersion "{BuildConfig.VERSION}"
#define MyAppPublisher "Deep-Live-Cam Team"
#define MyAppURL "https://github.com/hacksider/Deep-Live-Cam"
#define MyAppExeName "{BuildConfig.PROJECT_NAME}.exe"

[Setup]
AppId={{{{8F3C2A1B-5D4E-4F6A-8B9C-0D1E2F3A4B5C}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
OutputDir=..\\dist
OutputBaseFilename={{#MyAppName}}-Setup-{{#MyAppVersion}}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "..\\dist\\{{#MyAppName}}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
'''

    iss_file.write_text(iss_content)
    log_success(f"Created {iss_file}")
    log_info("Compile with: iscc build/installer.iss")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deep-Live-Cam Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build.py                      # Build for current platform (onedir)
    python build.py --mode onefile       # Single executable
    python build.py --platform windows   # Cross-compile for Windows
    python build.py --clean              # Clean build artifacts
    python build.py --github-workflow    # Create GitHub Actions workflow
    python build.py --inno-setup         # Create Windows installer script
        """,
    )

    parser.add_argument(
        "--platform",
        choices=["native", "windows", "linux", "macos"],
        default="native",
        help="Target platform (default: native)",
    )

    parser.add_argument(
        "--mode",
        choices=["onefile", "onedir"],
        default="onedir",
        help="Build mode: onefile or onedir (default: onedir)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable console output for debugging",
    )

    parser.add_argument(
        "--no-upx",
        action="store_true",
        help="Disable UPX compression",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts and exit",
    )

    parser.add_argument(
        "--github-workflow",
        action="store_true",
        help="Generate GitHub Actions workflow file",
    )

    parser.add_argument(
        "--inno-setup",
        action="store_true",
        help="Generate Inno Setup installer script",
    )

    args = parser.parse_args()

    # Handle special actions
    if args.clean:
        clean_build_artifacts()
        return 0

    if args.github_workflow:
        create_github_workflow()
        return 0

    if args.inno_setup:
        create_inno_setup_script()
        return 0

    # Check dependencies
    if not check_dependencies():
        return 1

    # Build
    success = False

    if args.platform == "native":
        success = build_native(
            mode=args.mode,
            debug=args.debug,
            upx=not args.no_upx,
        )
    elif args.platform == "windows" and platform.system() != "Windows":
        success = build_windows_cross()
    else:
        # Native build with explicit platform
        success = build_native(
            mode=args.mode,
            debug=args.debug,
            upx=not args.no_upx,
        )

    if success:
        log_header("BUILD SUCCESSFUL")
        log_info(f"Output directory: {BuildConfig.DIST_DIR}")

        # Show next steps
        log_info("\nNext steps:")
        if platform.system() == "Windows":
            log_info("  1. Test: dist\\Deep-Live-Cam\\Deep-Live-Cam.exe")
            log_info(
                "  2. Create installer: python build.py --inno-setup && iscc build/installer.iss"
            )
        else:
            log_info(
                f"  1. Test: dist/{BuildConfig.PROJECT_NAME}/{BuildConfig.PROJECT_NAME}"
            )
            log_info(
                "  2. Create archive: tar -czvf Deep-Live-Cam-Linux.tar.gz -C dist Deep-Live-Cam"
            )

        return 0
    else:
        log_header("BUILD FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
