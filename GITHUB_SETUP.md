# Hướng dẫn đưa lên GitHub và sử dụng

## 📤 Đưa lên GitHub

### 1. Tạo repository trên GitHub

1. Đăng nhập vào GitHub
2. Tạo repository mới (New repository)
3. Đặt tên: `internal_management` hoặc tên bạn muốn
4. Chọn Public hoặc Private
5. **KHÔNG** tích vào "Initialize with README" (vì đã có README.md)
6. Click "Create repository"

### 2. Khởi tạo Git và push code

Mở terminal/cmd trong thư mục dự án và chạy:

```bash
# Khởi tạo Git repository
git init

# Thêm tất cả file (trừ những file trong .gitignore)
git add .

# Commit lần đầu
git commit -m "Initial commit: Hệ thống Quản lý Nội bộ"

# Thêm remote (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/internal_management.git

# Push lên GitHub
git branch -M main
git push -u origin main
```

### 3. Các lệnh Git thường dùng

```bash
# Xem trạng thái
git status

# Thêm file đã thay đổi
git add .

# Commit thay đổi
git commit -m "Mô tả thay đổi"

# Push lên GitHub
git push

# Pull từ GitHub
git pull
```

## 📥 Sử dụng từ GitHub

### Clone về máy mới

```bash
git clone https://github.com/YOUR_USERNAME/internal_management.git
cd internal_management
```

### Cài đặt và chạy

**Windows:**
```bash
install_dependencies.bat
run.bat
```

**Linux/Mac:**
```bash
chmod +x install_dependencies.sh install_dependencies.sh run.sh
./install_dependencies.sh
./run.sh
```

## ⚠️ Lưu ý quan trọng

1. **KHÔNG commit dữ liệu thực tế:**
   - File `.gitignore` đã được cấu hình để loại trừ dữ liệu trong thư mục `data/`
   - Chỉ commit code, không commit dữ liệu người dùng

2. **Backup dữ liệu:**
   - Dữ liệu quan trọng nằm trong thư mục `data/`
   - Backup thư mục này riêng biệt, không dùng Git cho dữ liệu

3. **Bảo mật:**
   - Repository Public sẽ hiển thị code cho mọi người
   - Đổi `SECRET_KEY` trong `app.py` trước khi commit
   - Đổi mật khẩu admin mặc định ngay khi cài đặt

4. **Cấu trúc thư mục:**
   - Các file `.gitkeep` được tạo để giữ cấu trúc thư mục
   - Khi clone về, thư mục sẽ trống và ứng dụng sẽ tự tạo dữ liệu mẫu

## 🔧 Troubleshooting

### Lỗi "Permission denied" trên Linux/Mac
```bash
chmod +x *.sh
```

### Lỗi "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Lỗi khi push lên GitHub
```bash
# Kiểm tra remote
git remote -v

# Set lại remote nếu cần
git remote set-url origin https://github.com/YOUR_USERNAME/internal_management.git
```

