@echo off
echo ========================================
echo   KHOI TAO GIT REPOSITORY
echo ========================================
echo.

cd /d "%~dp0"

REM Kiểm tra Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git chua duoc cai dat!
    echo Vui long cai dat Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Kiểm tra xem đã là git repository chưa
if exist .git (
    echo [OK] Git repository da ton tai
    git remote -v
) else (
    echo Dang khoi tao Git repository...
    git init
    echo [OK] Da khoi tao Git repository
    
    echo.
    echo Them remote origin...
    git remote add origin https://github.com/DucVuong2901/internal_management.git
    echo [OK] Da them remote origin
)

echo.
echo ========================================
echo   HOAN TAT!
echo ========================================
echo.
echo Bay gio ban co the:
echo 1. Mo GitHub Desktop
echo 2. File -^> Add Local Repository
echo 3. Chon thu muc: %CD%
echo 4. Commit va Publish len GitHub
echo.
echo Hoac chay: push_to_github.bat de push truc tiep
echo.
pause

