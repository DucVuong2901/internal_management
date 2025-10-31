@echo off
echo ========================================
echo   Setup Git Repository
echo ========================================
echo.

REM Kiểm tra Git đã được cài đặt chưa
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git chua duoc cai dat!
    echo Vui long cai dat Git truoc:
    echo   Download tu: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git version:
git --version
echo.

REM Khởi tạo Git repository nếu chưa có
if not exist .git (
    echo Khoi tao Git repository...
    git init
    echo [OK] Git repository da duoc khoi tao
) else (
    echo [OK] Git repository da ton tai
)

echo.
echo ========================================
echo   Cac buoc tiep theo:
echo ========================================
echo.
echo 1. Tao repository tren GitHub:
echo    - Dang nhap GitHub
echo    - Tao repository moi (khong tich 'Initialize with README')
echo    - Copy URL repository
echo.
echo 2. Them remote va push:
echo    git remote add origin https://github.com/YOUR_USERNAME/internal_management.git
echo    git add .
echo    git commit -m "Initial commit"
echo    git branch -M main
echo    git push -u origin main
echo.
echo Hoac xem file GITHUB_SETUP.md de biet huong dan chi tiet
echo.

pause

