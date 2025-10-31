@echo off
echo ========================================
echo   AUTO PUSH CODE LEN GITHUB
echo ========================================
echo.

cd /d "%~dp0"

REM Kiểm tra Git
where git >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   KHONG TIM THAY GIT!
    echo ========================================
    echo.
    echo Ban co 2 lua chon:
    echo.
    echo [1] Cai dat Git (khuyen dung)
    echo      - Tai: https://git-scm.com/download/win
    echo      - Cai dat va khoi dong lai Command Prompt
    echo      - Chay lai script nay
    echo.
    echo [2] Su dung GitHub Desktop (de hon)
    echo      1. Mo GitHub Desktop
    echo      2. File -^> Add Local Repository
    echo      3. Chon: D:\internal_management
    echo      4. Commit va Publish
    echo.
    echo Xem file GITHUB_DESKTOP_GUIDE.md de biet chi tiet
    echo.
    pause
    exit /b 1
)

echo [OK] Git da san sang
git --version
echo.

REM Khởi tạo Git nếu chưa có
if not exist .git (
    echo Khoi tao Git repository...
    git init
    echo [OK] Da khoi tao
    echo.
)

REM Thêm remote
git remote remove origin 2>nul
git remote add origin https://github.com/DucVuong2901/internal_management.git
echo [OK] Remote da duoc cau hinh
echo.

REM Add file
echo Dang them file...
git add .
echo [OK] Da them file
echo.

REM Commit
echo Dang commit...
git commit -m "Initial commit: He thong Quan ly Noi bo - Support Windows and Linux" 2>nul
if errorlevel 1 (
    echo [WARNING] Co the da co commit roi
) else (
    echo [OK] Da commit
)
echo.

REM Set branch
git branch -M main
echo.

REM Push
echo ========================================
echo   DANG PUSH LEN GITHUB...
echo ========================================
echo.
echo Neu can authentication:
echo - Username: DucVuong2901
echo - Password: Personal Access Token
echo   (Tao tai: https://github.com/settings/tokens)
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo [LOI] Push that bai!
    echo.
    echo Giai phap:
    echo 1. Su dung GitHub Desktop (de hon - xem GITHUB_DESKTOP_GUIDE.md)
    echo 2. Tao Personal Access Token va su dung khi push
    echo 3. Hoac: git pull origin main --allow-unrelated-histories
    echo    roi chay lai: git push -u origin main
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo   THANH CONG!
    echo ========================================
    echo.
    echo Code da duoc push len GitHub!
    echo Xem tai: https://github.com/DucVuong2901/internal_management
    echo.
)

pause

