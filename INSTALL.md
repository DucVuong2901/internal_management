# Hướng dẫn Cài đặt và Chạy Ứng dụng

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Package manager của Python)

## Các bước cài đặt

### 1. Sao chép toàn bộ thư mục dự án

Sao chép toàn bộ thư mục `internal_management` sang máy mới. Đảm bảo bao gồm tất cả các thư mục và file sau:

```
internal_management/
├── app.py                 # File chính của ứng dụng
├── csv_storage.py         # Module quản lý user (CSV)
├── file_storage.py        # Module quản lý notes/docs (file)
├── requirements.txt       # Danh sách thư viện cần cài
├── users.csv             # Database người dùng (QUAN TRỌNG!)
├── README.md              # Tài liệu
├── INSTALL.md            # File này
├── run.bat               # Script chạy nhanh (Windows)
├── data/                 # THƯ MỤC DỮ LIỆU (QUAN TRỌNG!)
│   ├── categories.json
│   ├── edit_logs.json
│   ├── metadata.json
│   ├── notes/
│   └── docs/
├── uploads/               # THƯ MỤC FILE ĐÍNH KÈM (QUAN TRỌNG!)
│   ├── notes/
│   └── docs/
├── templates/            # Templates HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── notes.html
│   ├── docs.html
│   ├── note_form.html
│   ├── doc_form.html
│   ├── view_note.html
│   ├── view_doc.html
│   ├── search.html
│   ├── login.html
│   ├── manage_users.html
│   ├── manage_categories.html
│   ├── edit_logs.html
│   └── user_form.html
└── static/               # CSS và JavaScript
    ├── style.css
    └── script.js
```

### 2. Mở Command Prompt / Terminal

**Windows:**
- Nhấn `Win + R`, gõ `cmd`, nhấn Enter
- Hoặc mở PowerShell

**Linux/Mac:**
- Mở Terminal

### 3. Di chuyển vào thư mục dự án

```bash
cd D:\internal_management
```

(Thay đổi đường dẫn tùy theo nơi bạn đặt thư mục)

### 4. Cài đặt các thư viện cần thiết

**Cách 1: Sử dụng script tự động (Khuyến nghị)**

**Windows:**
```bash
install_dependencies.bat
```

**Linux/Mac:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**Cách 2: Cài đặt thủ công**

```bash
pip install -r requirements.txt
```

**Lưu ý:** 
- Nếu gặp lỗi quyền, thử:
  ```bash
  pip install --user -r requirements.txt
  ```
- Nếu gặp lỗi "ModuleNotFoundError: No module named 'flask'", chạy lại lệnh cài đặt trên
- Đảm bảo bạn đang ở đúng thư mục dự án khi chạy lệnh

### 5. Chạy ứng dụng

**Cách 1: Sử dụng script tự động (Windows)**
```bash
run.bat
```

**Cách 2: Chạy thủ công**
```bash
python app.py
```

### 6. Truy cập ứng dụng

Mở trình duyệt và truy cập:
- http://localhost:5000
- http://127.0.0.1:5000

## Thông tin đăng nhập mặc định

- **Username:** admin
- **Password:** admin

⚠️ **LƯU Ý BẢO MẬT:** Đổi mật khẩu ngay sau lần đăng nhập đầu tiên!

## Kiểm tra dữ liệu

Sau khi chạy, kiểm tra:
1. Đăng nhập thành công với tài khoản admin
2. Xem dashboard có hiển thị đúng số lượng notes/docs
3. Kiểm tra các ghi chú và tài liệu có hiển thị đầy đủ
4. Kiểm tra file đính kèm có thể xem được

## Xử lý lỗi thường gặp

### Lỗi: "Module not found"
**Nguyên nhân:** Chưa cài đặt thư viện
**Giải pháp:** Chạy lại `pip install -r requirements.txt`

### Lỗi: "Port 5000 already in use"
**Nguyên nhân:** Port 5000 đang được sử dụng bởi ứng dụng khác
**Giải pháp:** 
- Tắt ứng dụng khác đang dùng port 5000
- Hoặc sửa port trong `app.py` (dòng cuối cùng)

### Lỗi: "File not found"
**Nguyên nhân:** Thiếu file dữ liệu hoặc template
**Giải pháp:** Đảm bảo đã sao chép đầy đủ tất cả thư mục `data/`, `templates/`, `static/`, `uploads/`

### Lỗi: "Permission denied"
**Nguyên nhân:** Không có quyền ghi vào thư mục
**Giải pháp:** 
- Chạy terminal với quyền Administrator (Windows)
- Hoặc thay đổi quyền thư mục (Linux/Mac)

## Backup và Restore dữ liệu

### Backup:
Sao chép các thư mục/file sau:
- `users.csv`
- `data/` (toàn bộ)
- `uploads/` (toàn bộ)

### Restore:
Thay thế các thư mục/file trên bằng bản backup của bạn.

## Cấu trúc Database

Ứng dụng sử dụng:
- **CSV file** (`users.csv`) cho dữ liệu người dùng
- **Text files** (`data/notes/*.txt`, `data/docs/*.txt`) cho nội dung notes/docs
- **JSON files** (`data/metadata.json`, `data/edit_logs.json`, `data/categories.json`) cho metadata
- **File system** (`uploads/notes/`, `uploads/docs/`) cho file đính kèm

Tất cả dữ liệu đều ở dạng file thường, dễ backup và chuyển đổi.

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Python version: `python --version` (phải >= 3.8)
2. Đã cài đặt đầy đủ dependencies: `pip list`
3. Các file quan trọng đã tồn tại: `users.csv`, `data/`, `templates/`, `static/`

## License

MIT License

