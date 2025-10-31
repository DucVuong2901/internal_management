#!/bin/bash

echo "========================================"
echo "  PUSH CODE LEN GITHUB"
echo "  Repository: https://github.com/DucVuong2901/internal_management.git"
echo "========================================"
echo ""

# Kiểm tra Git
if ! command -v git &> /dev/null; then
    echo "ERROR: Git chưa được cài đặt!"
    echo ""
    echo "Vui lòng cài đặt Git:"
    echo "  Ubuntu/Debian: sudo apt-get install git"
    echo "  macOS: brew install git"
    exit 1
fi

echo "[OK] Git đã được cài đặt"
git --version
echo ""

# Di chuyển đến thư mục script
cd "$(dirname "$0")"

# Kiểm tra xem đã là git repository chưa
if [ ! -d .git ]; then
    echo "Khởi tạo Git repository..."
    git init
    echo "[OK] Đã khởi tạo Git repository"
    echo ""
fi

# Thêm remote (nếu chưa có)
if ! git remote | grep -q "origin"; then
    echo "Thêm remote origin..."
    git remote add origin https://github.com/DucVuong2901/internal_management.git
    echo "[OK] Đã thêm remote origin"
else
    echo "Kiểm tra remote..."
    git remote set-url origin https://github.com/DucVuong2901/internal_management.git
    echo "[OK] Đã cập nhật remote origin"
fi
echo ""

# Add tất cả file
echo "Đang thêm file vào Git..."
git add .
echo "[OK] Đã thêm file"
echo ""

# Commit
echo "Đang commit..."
git commit -m "Initial commit: Hệ thống Quản lý Nội bộ - Support Windows and Linux" || echo "WARNING: Có thể đã có commit rồi hoặc không có thay đổi"

# Set branch main
git branch -M main
echo ""

# Push lên GitHub
echo "========================================"
echo "  Đang push lên GitHub..."
echo "  Nếu cần authentication, vui lòng nhập:"
echo "  - Username: DucVuong2901"
echo "  - Password: Personal Access Token (không phải mật khẩu GitHub)"
echo "========================================"
echo ""

git push -u origin main

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "  LỖI: Push thất bại!"
    echo "========================================"
    echo ""
    echo "Các nguyên nhân có thể:"
    echo "1. Chưa được xác thực với GitHub"
    echo "2. Chưa có quyền truy cập repository"
    echo "3. Repository đã có code (cần pull trước)"
    echo ""
    echo "Giải pháp:"
    echo "1. Tạo Personal Access Token tại:"
    echo "   https://github.com/settings/tokens"
    echo "2. Sử dụng token đó thay vì mật khẩu khi push"
    echo "3. Hoặc sử dụng: git pull origin main --allow-unrelated-histories"
    echo "   trước khi push"
    echo ""
    exit 1
else
    echo ""
    echo "========================================"
    echo "  THÀNH CÔNG!"
    echo "========================================"
    echo ""
    echo "Code đã được push lên GitHub thành công!"
    echo "Xem tại: https://github.com/DucVuong2901/internal_management"
    echo ""
fi

