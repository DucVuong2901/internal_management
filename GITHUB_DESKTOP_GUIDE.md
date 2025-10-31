# Hướng dẫn sử dụng GitHub Desktop để Push Code

## 📦 Cách 1: Add Repository hiện có vào GitHub Desktop

### Bước 1: Add Repository
1. Trong GitHub Desktop, click **File** → **Add Local Repository**
2. Hoặc click **"+"** → **"Add Existing Repository"**
3. Chọn thư mục: `D:\internal_management`
4. Click **"Add Repository"**

### Bước 2: Khởi tạo Git (nếu chưa có)
Nếu GitHub Desktop báo "This directory does not appear to be a Git repository":
1. Click **"create a repository"** hoặc
2. Chạy lệnh trong terminal: `git init` trong thư mục `D:\internal_management`

### Bước 3: Push lên GitHub
1. Trong GitHub Desktop, bạn sẽ thấy tất cả file cần commit
2. Ở dưới bên trái, nhập commit message:
   ```
   Initial commit: Hệ thống Quản lý Nội bộ - Support Windows and Linux
   ```
3. Click nút **"Commit to main"** (hoặc **"Commit to master"**)
4. Click **"Publish repository"** (nút ở trên)
5. Đảm bảo URL là: `https://github.com/DucVuong2901/internal_management.git`
6. Có thể chọn **"Keep this code private"** hoặc để **Public**
7. Click **"Publish Repository"**

## 📤 Cách 2: Sử dụng Command Line (nếu GitHub Desktop không hoạt động)

Mở Terminal trong GitHub Desktop hoặc Command Prompt:

```cmd
cd D:\internal_management

REM Khởi tạo Git (nếu chưa có)
git init

REM Thêm remote
git remote add origin https://github.com/DucVuong2901/internal_management.git

REM Thêm file
git add .

REM Commit
git commit -m "Initial commit: Hệ thống Quản lý Nội bộ - Support Windows and Linux"

REM Set branch main
git branch -M main

REM Push lên GitHub
git push -u origin main
```

## ✅ Sau khi push thành công

Kiểm tra tại: https://github.com/DucVuong2901/internal_management

Bạn sẽ thấy tất cả code đã được upload!

## 🔄 Cập nhật code sau này

Sau khi code đã được push, để cập nhật:

**Với GitHub Desktop:**
1. Sửa code
2. Commit với message mô tả thay đổi
3. Click **"Push origin"** để đẩy lên GitHub

**Với Command Line:**
```cmd
git add .
git commit -m "Mô tả thay đổi"
git push
```

