@echo off
echo ========================================
echo   PUSH CODE LEN GITHUB
echo   Repository: https://github.com/DucVuong2901/internal_management.git
echo ========================================
echo.

REM Kiểm tra Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git chua duoc cai dat hoac chua co trong PATH!
    echo.
    echo Vui long:
    echo 1. Cai dat Git: https://git-scm.com/download/win
    echo 2. Khoi dong lai Command Prompt
    echo 3. Chay lai script nay
    pause
    exit /b 1
)

echo [OK] Git da duoc cai dat
git --version
echo.

cd /d "%~dp0"

REM Kiểm tra xem đã là git repository chưa
if not exist .git (
    echo Khoi tao Git repository...
    git init
    echo [OK] Da khoi tao Git repository
    echo.
)

REM Thêm remote (nếu chưa có)
git remote -v | findstr "origin" >nul
if errorlevel 1 (
    echo Them remote origin...
    git remote add origin https://github.com/DucVuong2901/internal_management.git
    echo [OK] Da them remote origin
) else (
    echo Kiem tra remote...
    git remote set-url origin https://github.com/DucVuong2901/internal_management.git
    echo [OK] Da cap nhat remote origin
)
echo.

REM Add tất cả file
echo Dang them file vao Git...
git add .
echo [OK] Da them file
echo.

REM Commit
echo Dang commit...
git commit -m "Initial commit: He thong Quan ly Noi bo - Support Windows and Linux"
if errorlevel 1 (
    echo.
    echo WARNING: Co the da co commit roi hoac khong co thay doi
    echo.
)

REM Set branch main
git branch -M main
echo.

REM Push lên GitHub
echo ========================================
echo   Dang push len GitHub...
echo   Neu can authentication, vui long nhap:
echo   - Username: DucVuong2901
echo   - Password: Personal Access Token (khong phai mat khau GitHub)
echo ========================================
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo   LOI: Push that bai!
    echo ========================================
    echo.
    echo Cac nguyen nhan co the:
    echo 1. Chua duoc xac thuc voi GitHub
    echo 2. Chua co quyen truy cap repository
    echo 3. Repository da co code (can pull truoc)
    echo.
    echo Giai phap:
    echo 1. Tao Personal Access Token tai:
    echo    https://github.com/settings/tokens
    echo 2. Su dung token do thay vi mat khau khi push
    echo 3. Hoac su dung: git pull origin main --allow-unrelated-histories
    echo    truoc khi push
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo   THANH CONG!
    echo ========================================
    echo.
    echo Code da duoc push len GitHub thanh cong!
    echo Xem tai: https://github.com/DucVuong2901/internal_management
    echo.
)

pause

