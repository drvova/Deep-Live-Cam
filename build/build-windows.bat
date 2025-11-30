@echo off
REM ============================================================
REM Deep-Live-Cam Windows Build Script
REM ============================================================
REM
REM Usage:
REM     build-windows.bat              - Build onedir (default)
REM     build-windows.bat onefile      - Build single executable
REM     build-windows.bat debug        - Build with console output
REM     build-windows.bat clean        - Clean build artifacts
REM
REM Requirements:
REM     - Python 3.10+
REM     - PyInstaller (pip install pyinstaller)
REM     - UPX (optional, for compression)
REM
REM ============================================================

setlocal EnableDelayedExpansion

REM Configuration
set PROJECT_NAME=Deep-Live-Cam
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set DIST_DIR=%PROJECT_ROOT%\dist
set BUILD_WORK=%SCRIPT_DIR%work

REM Colors (Windows 10+)
set GREEN=[92m
set RED=[91m
set YELLOW=[93m
set CYAN=[96m
set RESET=[0m

echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%  Deep-Live-Cam Windows Build System%RESET%
echo %CYAN%============================================================%RESET%
echo.

REM Parse arguments
set MODE=onedir
set DEBUG=0
set CLEAN=0

if "%1"=="onefile" set MODE=onefile
if "%1"=="debug" set DEBUG=1
if "%1"=="clean" set CLEAN=1

REM Handle clean
if %CLEAN%==1 (
    echo %YELLOW%[INFO] Cleaning build artifacts...%RESET%
    if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
    if exist "%BUILD_WORK%" rmdir /s /q "%BUILD_WORK%"
    if exist "%PROJECT_ROOT%\*.spec" del /q "%PROJECT_ROOT%\*.spec"
    echo %GREEN%[SUCCESS] Clean complete%RESET%
    goto :end
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR] Python not found. Please install Python 3.10+%RESET%
    exit /b 1
)
echo %GREEN%[OK] Python found%RESET%

REM Check PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[INFO] Installing PyInstaller...%RESET%
    pip install pyinstaller
)
echo %GREEN%[OK] PyInstaller ready%RESET%

REM Change to project root
cd /d "%PROJECT_ROOT%"

REM Build command construction
set PYINSTALLER_CMD=python -m PyInstaller
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --clean --noconfirm
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --name=%PROJECT_NAME%
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --distpath="%DIST_DIR%"
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --workpath="%BUILD_WORK%"
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --specpath="%SCRIPT_DIR%"

REM Build mode
if "%MODE%"=="onefile" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --onefile
    echo %CYAN%[INFO] Building single executable (onefile)%RESET%
) else (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --onedir
    echo %CYAN%[INFO] Building directory package (onedir)%RESET%
)

REM Console mode
if %DEBUG%==1 (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --console
    echo %YELLOW%[DEBUG] Console output enabled%RESET%
) else (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --windowed
)

REM Icon
if exist "%PROJECT_ROOT%\media\icon.ico" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --icon="%PROJECT_ROOT%\media\icon.ico"
)

REM Data files (Windows uses ; separator)
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --add-data="modules\ui\theme.json;modules\ui"
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --add-data="locales;locales"
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --add-data="media;media"
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --add-data="tkinter_fix.py;."

REM Hidden imports
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.core
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.core.app
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.config
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.config.globals
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.face
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.face.analyser
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.media
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.media.ffmpeg
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.processors
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.processors.registry
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.processors.frame
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.processors.frame.swapper
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.ui
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.ui.app
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=modules.i18n
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=cv2
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=numpy
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=PIL
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=customtkinter
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=tkinter
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=onnxruntime
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=insightface
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=torch
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=psutil

REM Collect all for problematic packages
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --collect-all=customtkinter
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --collect-all=onnxruntime

REM Excludes
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --exclude-module=matplotlib
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --exclude-module=pandas
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --exclude-module=IPython
set PYINSTALLER_CMD=%PYINSTALLER_CMD% --exclude-module=jupyter

REM Entry script
set PYINSTALLER_CMD=%PYINSTALLER_CMD% run.py

echo.
echo %CYAN%[INFO] Starting build...%RESET%
echo.

REM Execute build
%PYINSTALLER_CMD%

if errorlevel 1 (
    echo.
    echo %RED%============================================================%RESET%
    echo %RED%  BUILD FAILED%RESET%
    echo %RED%============================================================%RESET%
    exit /b 1
)

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%  BUILD SUCCESSFUL%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo %CYAN%Output location:%RESET%
echo     %DIST_DIR%\%PROJECT_NAME%
echo.
echo %CYAN%To run:%RESET%
echo     %DIST_DIR%\%PROJECT_NAME%\%PROJECT_NAME%.exe
echo.
echo %CYAN%To create installer:%RESET%
echo     iscc "%SCRIPT_DIR%installer.iss"
echo.

:end
endlocal
