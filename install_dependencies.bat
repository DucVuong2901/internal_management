@echo off
echo ========================================
echo   CAI DAT DEPENDENCIES
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python khong duoc tim thay!
    echo Vui long cai dat Python 3.8 tro len truoc.
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

echo Installing dependencies from requirements.txt...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Khong the cai dat dependencies!
    echo ========================================
    echo.
    echo Thu cac cach sau:
    echo 1. Chay voi quyen Administrator
    echo 2. Su dung: pip install --user -r requirements.txt
    echo 3. Kiem tra ket noi mang
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo   CAI DAT THANH CONG!
    echo ========================================
    echo.
    echo Ban co the chay ung dung bang:
    echo   python app.py
    echo   HOAC
    echo   run.bat
    echo.
)

pause

