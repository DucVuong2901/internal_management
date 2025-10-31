# Script tự động push code lên GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTO PUSH CODE LEN GITHUB" -ForegroundColor Cyan
Write-Host "  Repository: https://github.com/DucVuong2901/internal_management.git" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Tìm Git từ các vị trí có thể
$gitPaths = @(
    "git",
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "$env:LOCALAPPDATA\GitHubDesktop\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles\GitHub CLI\gh.exe"
)

$gitExe = $null
foreach ($path in $gitPaths) {
    try {
        if ($path -eq "git") {
            $gitExe = Get-Command git -ErrorAction SilentlyContinue
            if ($gitExe) {
                $gitExe = "git"
                break
            }
        } elseif (Test-Path $path) {
            $gitExe = $path
            break
        }
    } catch {
        continue
    }
}

if (-not $gitExe) {
    Write-Host "ERROR: Khong tim thay Git!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vui long:" -ForegroundColor Yellow
    Write-Host "1. Cai dat Git: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "2. Hoac su dung GitHub Desktop de push code" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Xem file GITHUB_DESKTOP_GUIDE.md de biet cach dung GitHub Desktop" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host "[OK] Da tim thay Git" -ForegroundColor Green
& $gitExe --version
Write-Host ""

# Di chuyển đến thư mục dự án
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Khởi tạo Git repository nếu chưa có
if (-not (Test-Path .git)) {
    Write-Host "Khoi tao Git repository..." -ForegroundColor Yellow
    & $gitExe init
    Write-Host "[OK] Da khoi tao Git repository" -ForegroundColor Green
    Write-Host ""
}

# Kiểm tra và thêm remote
$remotes = & $gitExe remote -v 2>&1
if ($remotes -notmatch "origin.*internal_management") {
    Write-Host "Them remote origin..." -ForegroundColor Yellow
    & $gitExe remote remove origin 2>$null
    & $gitExe remote add origin https://github.com/DucVuong2901/internal_management.git
    Write-Host "[OK] Da them remote origin" -ForegroundColor Green
} else {
    Write-Host "[OK] Remote origin da ton tai" -ForegroundColor Green
}
Write-Host ""

# Add tất cả file
Write-Host "Dang them file vao Git..." -ForegroundColor Yellow
& $gitExe add .
Write-Host "[OK] Da them file" -ForegroundColor Green
Write-Host ""

# Commit
Write-Host "Dang commit..." -ForegroundColor Yellow
$commitMessage = "Initial commit: He thong Quan ly Noi bo - Support Windows and Linux"
$commitResult = & $gitExe commit -m $commitMessage 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Da commit" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Co the da co commit roi hoac khong co thay doi" -ForegroundColor Yellow
}
Write-Host ""

# Set branch main
& $gitExe branch -M main 2>$null
Write-Host ""

# Push lên GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DANG PUSH LEN GITHUB..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Neu can authentication:" -ForegroundColor Yellow
Write-Host "- Username: DucVuong2901" -ForegroundColor Yellow
Write-Host "- Password: Personal Access Token (tao tai https://github.com/settings/tokens)" -ForegroundColor Yellow
Write-Host ""

$pushResult = & $gitExe push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  THANH CONG!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Code da duoc push len GitHub thanh cong!" -ForegroundColor Green
    Write-Host "Xem tai: https://github.com/DucVuong2901/internal_management" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  LOI: Push that bai!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host $pushResult -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Cac nguyen nhan co the:" -ForegroundColor Yellow
    Write-Host "1. Chua duoc xac thuc voi GitHub" -ForegroundColor Yellow
    Write-Host "2. Chua co quyen truy cap repository" -ForegroundColor Yellow
    Write-Host "3. Repository da co code (can pull truoc)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Giai phap:" -ForegroundColor Cyan
    Write-Host "1. Su dung GitHub Desktop de push (de hon)" -ForegroundColor Cyan
    Write-Host "2. Tao Personal Access Token va su dung khi push" -ForegroundColor Cyan
    Write-Host "3. Hoac chay: git pull origin main --allow-unrelated-histories" -ForegroundColor Cyan
    Write-Host ""
}

pause

