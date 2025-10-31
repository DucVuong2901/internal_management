# Hướng dẫn Di chuyển từ Windows sang Linux

## ✅ Tính tương thích

Code đã được thiết kế để tương thích hoàn toàn giữa Windows và Linux:

- ✅ Tất cả file operations sử dụng UTF-8 encoding
- ✅ Đường dẫn được normalize thành absolute path
- ✅ Sử dụng `os.path.join()` cho cross-platform paths
- ✅ Atomic file writes với `os.replace()` (tương thích đa nền tảng)

## Các bước di chuyển

### 1. Sao chép dữ liệu

Sao chép toàn bộ thư mục `internal_management` từ Windows sang Linux:

```bash
# Trên Windows, nén thư mục hoặc dùng scp/rsync
# Ví dụ: scp -r internal_management user@linux-server:/path/to/
```

**Các file/thư mục quan trọng cần sao chép:**
- ✅ `data/` (gồm notes, docs, metadata.json, categories.json, edit_logs.json)
- ✅ `uploads/` (file đính kèm)
- ✅ `users.csv` (database người dùng)
- ✅ Tất cả file Python (.py)
- ✅ `templates/` và `static/`
- ✅ `requirements.txt`

### 2. Cài đặt trên Linux

```bash
# Di chuyển vào thư mục dự án
cd /path/to/internal_management

# Cấp quyền thực thi cho script
chmod +x run.sh
chmod +x install_dependencies.sh

# Cài đặt dependencies
./install_dependencies.sh

# Hoặc cài thủ công:
pip3 install -r requirements.txt
```

### 3. Kiểm tra quyền truy cập

Đảm bảo thư mục có quyền ghi:

```bash
# Kiểm tra quyền hiện tại
ls -la data/
ls -la uploads/

# Nếu cần, cấp quyền ghi (thay user bằng tên user Linux của bạn)
chmod -R u+w data/ uploads/
chown -R $USER:$USER data/ uploads/
```

### 4. Chạy ứng dụng

```bash
# Cách 1: Sử dụng script
./run.sh

# Cách 2: Chạy trực tiếp
python3 app.py

# Cách 3: Chạy ở background (cho production)
nohup python3 app.py > app.log 2>&1 &
```

### 5. Cấu hình tên miền (tùy chọn)

```bash
# Set biến môi trường
export DOMAIN_NAME=yourdomain.com
# Hoặc set IP:
export DOMAIN_NAME=192.168.1.100

# Sau đó chạy
python3 app.py
```

## Lưu ý quan trọng

### ✅ Dữ liệu đã có trên Windows

- **Metadata JSON**: Hoạt động tốt vì đã dùng UTF-8
- **Files ghi chú/tài liệu (.txt)**: Tương thích hoàn toàn
- **CSV users**: Tương thích (đã dùng UTF-8 và `newline=''`)
- **Line endings**: Python tự động xử lý, không cần lo lắng

### ⚠️ Khác biệt cần lưu ý

1. **Đường dẫn**: Code đã tự động chuyển đổi
   - Windows: `D:\internal_management\data\notes`
   - Linux: `/path/to/internal_management/data/notes`

2. **Quyền file**: Linux có phân quyền rõ ràng hơn
   - Đảm bảo user chạy app có quyền đọc/ghi
   - Thư mục `data/` và `uploads/` cần quyền ghi

3. **Port**: Mặc định là port 5001, có thể thay đổi:
   ```bash
   export PORT=8080
   python3 app.py
   ```

### 🔍 Kiểm tra sau khi chuyển

1. **Kiểm tra file metadata**:
   ```bash
   cat data/metadata.json
   ```

2. **Kiểm tra user data**:
   ```bash
   cat users.csv
   ```

3. **Kiểm tra ghi chú/tài liệu**:
   ```bash
   ls -la data/notes/
   ls -la data/docs/
   ```

4. **Kiểm tra log lỗi**: Nếu có lỗi, xem log:
   ```bash
   tail -f app.log  # Nếu chạy với nohup
   ```

## Troubleshooting

### Lỗi Permission Denied

```bash
# Giải pháp:
chmod -R u+w data/ uploads/
# Hoặc:
sudo chown -R $USER:$USER data/ uploads/
```

### Lỗi encoding

Code đã dùng UTF-8, nhưng nếu gặp vấn đề:

```python
# File được mở với encoding='utf-8', nên không có vấn đề
```

### Port đã được sử dụng

```bash
# Thay đổi port:
export PORT=8080
python3 app.py
```

### Không tìm thấy module

```bash
# Đảm bảo đã cài dependencies:
pip3 install -r requirements.txt

# Hoặc dùng virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ví dụ chuyển đổi hoàn chỉnh

```bash
# 1. Trên máy Windows, tạo file zip
# (hoặc dùng scp/rsync)

# 2. Trên Linux, giải nén hoặc nhận file
cd /opt
mkdir internal_management
cd internal_management
# Copy files vào đây

# 3. Cài đặt
chmod +x *.sh
./install_dependencies.sh

# 4. Cấp quyền
chmod -R u+w data/ uploads/

# 5. Chạy
./run.sh

# 6. Truy cập
# http://your-server-ip:5001
```

## Kết luận

✅ **Code hoàn toàn tương thích giữa Windows và Linux**

- Dữ liệu được test trên Windows có thể chạy ngay trên Linux
- Không cần convert hay migrate dữ liệu
- Chỉ cần sao chép file và cài đặt dependencies

Chúc bạn thành công! 🚀

