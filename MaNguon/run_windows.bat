@echo off
chcp 65001 >nul
setlocal
set PYTHONUTF8=1
cd /d "%~dp0"

set "PY_CMD="
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py -3"
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=python"
    ) else (
        python3 --version >nul 2>&1
        if not errorlevel 1 (
            set "PY_CMD=python3"
        )
    )
)

if "%PY_CMD%"=="" (
    echo [!] Khong tim thay Python 3 tren may Windows nay.
    echo     Vui long cai Python 3 tai: https://www.python.org/downloads/
    echo     Luu y: Tick chon "Add python.exe to PATH" trong trinh cai dat.
    echo.
    pause
    exit /b 1
)

%PY_CMD% main.py %*
if errorlevel 1 (
    echo.
    echo [!] Chuong trinh ket thuc voi ma loi %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)
endlocal
