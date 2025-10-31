@echo off
echo ========================================
echo   HE THONG QUAN LY NOI BO
echo   Starting Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python khong duoc tim thay!
    echo Vui long cai dat Python 3.8 tro len.
    pause
    exit /b 1
)

echo Checking Python version...
python --version

echo.
echo Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Dependencies chua duoc cai dat!
    echo Dang cai dat dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Khong the cai dat dependencies!
        pause
        exit /b 1
    )
    echo Dependencies da duoc cai dat thanh cong!
) else (
    echo Dependencies da san sang!
)

echo.
echo ========================================
echo   Starting Flask Application...
if defined DOMAIN_NAME (
    echo   Using domain: %DOMAIN_NAME%
    echo   Access at: http://%DOMAIN_NAME%:5001
) else (
    echo   Access at: http://localhost:5001
    echo   To use custom domain: set DOMAIN_NAME=yourdomain.com
)
echo   Press CTRL+C to stop
echo ========================================
echo.

python app.py

pause

