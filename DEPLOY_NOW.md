# 🚀 Deploy Code Lên GitHub Ngay

**Repository:** https://github.com/DucVuong2901/internal_management.git

## ⚠️ Trạng thái hiện tại

Code **CHƯA** được push lên GitHub. Git repository chưa được khởi tạo.

## 📋 Hướng dẫn deploy

### Bước 1: Cài đặt Git (nếu chưa có)

**Windows:**
1. Tải Git: https://git-scm.com/download/win
2. Cài đặt (giữ nguyên tất cả options mặc định)
3. Khởi động lại Command Prompt/PowerShell

**Kiểm tra đã cài đặt:**
```cmd
git --version
```

### Bước 2: Chạy script tự động

**Windows:**
```cmd
cd D:\internal_management
push_to_github.bat
```

**Linux/Mac:**
```bash
cd /path/to/internal_management
chmod +x push_to_github.sh
./push_to_github.sh
```

### Bước 3: Xác thực với GitHub (nếu cần)

Khi được hỏi authentication:

1. **Username:** `DucVuong2901`

2. **Password:** Personal Access Token (KHÔNG phải mật khẩu GitHub)
   - Tạo token tại: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Chọn quyền: `repo` (full control of private repositories)
   - Copy token và dán vào khi được hỏi password

## 🔧 Deploy thủ công (nếu script không hoạt động)

Mở Command Prompt/PowerShell trong thư mục `D:\internal_management`:

```cmd
REM 1. Khởi tạo Git
git init

REM 2. Thêm remote
git remote add origin https://github.com/DucVuong2901/internal_management.git

REM 3. Thêm file
git add .

REM 4. Commit
git commit -m "Initial commit: Hệ thống Quản lý Nội bộ - Support Windows and Linux"

REM 5. Set branch main
git branch -M main

REM 6. Push lên GitHub
git push -u origin main
```

**Linux/Mac:**
```bash
# 1. Khởi tạo Git
git init

# 2. Thêm remote
git remote add origin https://github.com/DucVuong2901/internal_management.git

# 3. Thêm file
git add .

# 4. Commit
git commit -m "Initial commit: Hệ thống Quản lý Nội bộ - Support Windows and Linux"

# 5. Set branch main
git branch -M main

# 6. Push lên GitHub
git push -u origin main
```

## ✅ Kiểm tra sau khi deploy

Sau khi push thành công, kiểm tra tại:
https://github.com/DucVuong2901/internal_management

Bạn sẽ thấy tất cả code đã được upload.

## ❓ Xử lý lỗi

### Lỗi: "Git is not recognized"
→ Cài đặt Git: https://git-scm.com/download/win

### Lỗi: "Permission denied" hoặc "Authentication failed"
→ Tạo Personal Access Token và sử dụng token đó thay vì mật khẩu

### Lỗi: "Repository not found"
→ Kiểm tra repository đã được tạo trên GitHub chưa
→ Kiểm tra bạn có quyền truy cập repository không

### Lỗi: "failed to push some refs"
→ Repository có thể đã có code, cần pull trước:
```cmd
git pull origin main --allow-unrelated-histories
git push -u origin main
```

