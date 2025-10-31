# Hướng dẫn Đóng gói để Chuyển sang Máy khác

## Bước 1: Kiểm tra các file cần thiết

Đảm bảo các file/thư mục sau đã tồn tại:

- ✅ `app.py`
- ✅ `csv_storage.py`
- ✅ `file_storage.py`
- ✅ `requirements.txt`
- ✅ `users.csv`
- ✅ `data/` (và tất cả file bên trong)
- ✅ `uploads/` (và tất cả file bên trong)
- ✅ `templates/` (và tất cả file bên trong)
- ✅ `static/` (và tất cả file bên trong)
- ✅ `README.md`
- ✅ `INSTALL.md`
- ✅ `run.bat` (hoặc `run.sh`)

## Bước 2: Đóng gói (Tạo file ZIP)

### Windows:

1. **Sử dụng File Explorer:**
   - Chọn thư mục `internal_management`
   - Click chuột phải → Send to → Compressed (zipped) folder
   - Đặt tên file: `internal_management_v1.0.zip` (hoặc tên khác)

2. **Sử dụng PowerShell:**
   ```powershell
   Compress-Archive -Path "D:\internal_management\*" -DestinationPath "D:\internal_management_backup.zip" -Force
   ```

### Linux/Mac:

```bash
cd /path/to/parent/directory
zip -r internal_management_backup.zip internal_management/ -x "*/__pycache__/*" "*/.git/*" "*/venv/*" "*/instance/*"
```

## Bước 3: Chuyển file ZIP sang máy mới

- Copy file ZIP qua USB, email, cloud storage, hoặc mạng nội bộ
- Hoặc sử dụng các dịch vụ: Google Drive, Dropbox, OneDrive, etc.

## Bước 4: Giải nén và chạy trên máy mới

### Windows:

1. Giải nén file ZIP vào thư mục (ví dụ: `D:\internal_management`)
2. Mở Command Prompt tại thư mục đó
3. Chạy: `run.bat`

### Linux/Mac:

1. Giải nén file ZIP:
   ```bash
   unzip internal_management_backup.zip -d /path/to/destination
   ```
2. Di chuyển vào thư mục:
   ```bash
   cd /path/to/destination/internal_management
   ```
3. Cho phép chạy script:
   ```bash
   chmod +x run.sh
   ```
4. Chạy ứng dụng:
   ```bash
   ./run.sh
   ```

## Lưu ý quan trọng

### ✅ NHỚ SAO CHÉP:

1. **`users.csv`** - Dữ liệu người dùng
2. **`data/`** - Toàn bộ thư mục (notes, docs, metadata, logs, categories)
3. **`uploads/`** - Toàn bộ thư mục (file đính kèm, hình ảnh)

### ❌ KHÔNG CẦN SAO CHÉP:

- `__pycache__/` - Sẽ tự động tạo lại
- `instance/` - Database SQLite cũ (không dùng nữa)
- `*.pyc` - File compiled Python
- `.git/` - Nếu sử dụng git (tùy chọn)

## Kiểm tra sau khi chuyển

1. **Kiểm tra dữ liệu:**
   - Đăng nhập với tài khoản admin (mật khẩu: admin)
   - Xem dashboard có hiển thị đúng số lượng notes/docs?
   - Kiểm tra các ghi chú và tài liệu có còn nguyên?
   - Kiểm tra file đính kèm có thể xem được không?

2. **Kiểm tra chức năng:**
   - Tạo mới ghi chú/tài liệu
   - Chỉnh sửa ghi chú/tài liệu
   - Upload file đính kèm
   - Xem hình ảnh preview

## Backup định kỳ

Khuyến nghị backup thường xuyên:

```bash
# Windows PowerShell
Compress-Archive -Path "D:\internal_management\users.csv,D:\internal_management\data,D:\internal_management\uploads" -DestinationPath "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"

# Linux/Mac
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz users.csv data/ uploads/
```

## Xử lý lỗi

Nếu gặp lỗi sau khi chuyển máy:

1. **Lỗi "Module not found":**
   - Chạy: `pip install -r requirements.txt`

2. **Lỗi "File not found":**
   - Kiểm tra lại các thư mục `data/`, `uploads/`, `templates/`, `static/`
   - Đảm bảo đã giải nén đầy đủ

3. **Lỗi "Permission denied":**
   - Kiểm tra quyền truy cập thư mục
   - Chạy với quyền Administrator (Windows)

## Kích thước ước tính

Một bản backup đầy đủ thường có kích thước:
- Code và templates: ~500 KB - 2 MB
- Dữ liệu (data/): Tùy thuộc số lượng notes/docs
- File đính kèm (uploads/): Tùy thuộc kích thước file

Ước tính tổng: 5-50 MB (tùy dữ liệu)

