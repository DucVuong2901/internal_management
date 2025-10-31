#!/bin/bash

# Script để setup Git và push lên GitHub

echo "========================================"
echo "  Setup Git Repository"
echo "========================================"
echo ""

# Kiểm tra Git đã được cài đặt chưa
if ! command -v git &> /dev/null; then
    echo "ERROR: Git chưa được cài đặt!"
    echo "Vui lòng cài đặt Git trước:"
    echo "  Ubuntu/Debian: sudo apt-get install git"
    echo "  macOS: brew install git"
    exit 1
fi

echo "Git version:"
git --version
echo ""

# Khởi tạo Git repository nếu chưa có
if [ ! -d .git ]; then
    echo "Khởi tạo Git repository..."
    git init
    echo "✓ Git repository đã được khởi tạo"
else
    echo "✓ Git repository đã tồn tại"
fi

echo ""
echo "========================================"
echo "  Các bước tiếp theo:"
echo "========================================"
echo ""
echo "1. Tạo repository trên GitHub:"
echo "   - Đăng nhập GitHub"
echo "   - Tạo repository mới (không tích 'Initialize with README')"
echo "   - Copy URL repository"
echo ""
echo "2. Thêm remote và push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/internal_management.git"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Hoặc xem file GITHUB_SETUP.md để biết hướng dẫn chi tiết"
echo ""

