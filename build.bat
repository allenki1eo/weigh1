@echo off
:: WeighMaster Pro — local Windows build script
:: Run this on a Windows machine that has Python 3.11 installed.
:: Output: dist\WeighMaster Pro\WeighMasterPro.exe

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ============================================================
echo  WeighMaster Pro — Windows Build
echo ============================================================

:: ── Check Python ────────────────────────────────────────────
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ and add to PATH.
    pause & exit /b 1
)

:: ── Install / upgrade dependencies ──────────────────────────
echo.
echo [1/4] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install "pyinstaller==6.11.0" --quiet
if errorlevel 1 ( echo ERROR: pip install failed & pause & exit /b 1 )

:: ── Download fonts ───────────────────────────────────────────
echo.
echo [2/4] Downloading fonts...
if not exist "weighmaster\assets\fonts" mkdir "weighmaster\assets\fonts"
python -c "
import urllib.request, zipfile, os, io, shutil

fonts_dir = 'weighmaster/assets/fonts'

def dl_zip(url, picks):
    try:
        print(f'  Downloading {url.split(\"/\")[-1]} ...')
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                base = os.path.basename(name)
                if base in picks:
                    dest = os.path.join(fonts_dir, base)
                    with z.open(name) as src, open(dest, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    print(f'    + {base}')
    except Exception as e:
        print(f'  WARNING: {e} — continuing without this font')

dl_zip(
    'https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip',
    {'JetBrainsMono-Regular.ttf', 'JetBrainsMono-Bold.ttf'}
)
dl_zip(
    'https://github.com/googlefonts/dm-fonts/releases/download/v1.100/fonts-dm-sans.zip',
    {'DMSans-Regular.ttf', 'DMSans-SemiBold.ttf', 'DMSans-Bold.ttf'}
)
print('  Fonts done.')
"

:: ── Run PyInstaller ──────────────────────────────────────────
echo.
echo [3/4] Building executable with PyInstaller...
pyinstaller weighmaster.spec --clean --noconfirm
if errorlevel 1 ( echo ERROR: PyInstaller failed & pause & exit /b 1 )

:: ── Verify ───────────────────────────────────────────────────
echo.
echo [4/4] Verifying output...
if exist "dist\WeighMaster Pro\WeighMasterPro.exe" (
    echo.
    echo ============================================================
    echo  BUILD SUCCESSFUL
    echo  Location: dist\WeighMaster Pro\WeighMasterPro.exe
    echo.
    echo  To deploy: copy the entire "dist\WeighMaster Pro\" folder
    echo  to the target machine. No Python installation required.
    echo ============================================================
) else (
    echo ERROR: WeighMasterPro.exe not found in dist\
    pause & exit /b 1
)

pause
