# Hệ thống Quản lý Nội bộ

Ứng dụng web Python với Flask để quản lý ghi chú, tài liệu nội bộ với giao diện thân thiện và hiện đại.

**Hỗ trợ đa nền tảng: Windows, Linux, macOS**

## 🚀 Cài đặt từ GitHub

### 1. Clone repository
```bash
git clone https://github.com/YOUR_USERNAME/internal_management.git
cd internal_management
```

### 2. Cài đặt dependencies

**Windows:**
```bash
install_dependencies.bat
```

**Linux/Mac:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**Hoặc cài đặt thủ công:**
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

Ứng dụng sẽ chạy tại: `http://localhost:5001`

### 4. Đăng nhập
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **LƯU Ý:** Đổi mật khẩu ngay sau lần đăng nhập đầu tiên!

## Tính năng

- ✅ **Dashboard**: Trang tổng quan với thống kê và các mục gần đây
- ✅ **Quản lý Ghi chú**: Tạo, chỉnh sửa, xóa ghi chú với phân loại và rich text editor
- ✅ **Tài liệu Nội bộ**: Quản lý tài liệu nội bộ với phân loại và rich text editor
- ✅ **Tìm kiếm**: Tìm kiếm trong cả ghi chú và tài liệu
- ✅ **Đính kèm File**: Upload và quản lý file/hình ảnh đính kèm cho ghi chú
- ✅ **Quản lý User**: Phân quyền admin/user/viewer
- ✅ **Quản lý Danh mục**: Admin định nghĩa danh mục, user chỉ chọn từ danh sách
- ✅ **Lịch sử chỉnh sửa**: Theo dõi lịch sử thay đổi chi tiết
- ✅ **Rich Text Editor**: Định dạng văn bản (in đậm, in nghiêng, màu sắc, kích thước)
- ✅ **Giao diện thân thiện**: Bootstrap 5 với thiết kế hiện đại
- ✅ **Responsive**: Tương thích với mọi thiết bị

## ⚙️ Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Package manager của Python)
- Git (để clone từ GitHub)

## 📦 Cài đặt từ source code

### Cách 1: Clone từ GitHub (Khuyên dùng)

1. **Clone repository:**
```bash
git clone https://github.com/YOUR_USERNAME/internal_management.git
cd internal_management
```

2. **Cài đặt dependencies và chạy:**

**Windows:**
```bash
# Cài đặt dependencies
install_dependencies.bat

# Chạy ứng dụng
run.bat
```

**Linux/Mac:**
```bash
# Cài đặt dependencies
chmod +x install_dependencies.sh
./install_dependencies.sh

# Chạy ứng dụng
chmod +x run.sh
./run.sh
```

**Hoặc chạy thủ công:**
```bash
pip install -r requirements.txt
python app.py
```

### Cách 2: Tải ZIP và giải nén

1. Tải ZIP từ GitHub
2. Giải nén vào thư mục bạn muốn
3. Mở terminal/cmd trong thư mục đó
4. Thực hiện các bước cài đặt như trên

**Lưu ý:** Khi clone từ GitHub, thư mục `data/` sẽ trống (chỉ có file `.gitkeep`). Ứng dụng sẽ tự tạo dữ liệu mẫu khi chạy lần đầu.

### Đưa code lên GitHub

**Repository:** https://github.com/DucVuong2901/internal_management.git

**Push code tự động:**

**Windows:**
```cmd
push_to_github.bat
```

**Linux/Mac:**
```bash
chmod +x push_to_github.sh
./push_to_github.sh
```

Xem file [GIT_QUICKSTART.md](GIT_QUICKSTART.md) để biết hướng dẫn nhanh hoặc [GITHUB_SETUP.md](GITHUB_SETUP.md) để biết hướng dẫn chi tiết.

### Cấu hình tên miền (Tùy chọn)

Để truy cập bằng tên miền thay vì localhost:

**Windows:**
```bash
set DOMAIN_NAME=mydomain.com
python app.py
```

**Linux/Mac:**
```bash
export DOMAIN_NAME=mydomain.com
python app.py
```

Xem file `config.example.txt` để biết hướng dẫn chi tiết.

### Thông tin đăng nhập mặc định
- **Username:** admin
- **Password:** admin

⚠️ **LƯU Ý:** Đổi mật khẩu ngay sau lần đăng nhập đầu tiên!

## Sử dụng

### Dashboard
- Xem tổng quan số lượng ghi chú và tài liệu
- Xem các mục gần đây
- Truy cập nhanh các chức năng

### Ghi chú
- Tạo ghi chú mới với tiêu đề, nội dung và danh mục
- Chỉnh sửa hoặc xóa ghi chú
- Tìm kiếm và lọc theo danh mục

### Tài liệu
- Tạo tài liệu nội bộ
- Quản lý và chỉnh sửa tài liệu
- Tìm kiếm và phân loại

### Tìm kiếm
- Tìm kiếm đồng thời trong ghi chú và tài liệu
- Thanh tìm kiếm ở header để tìm nhanh

## Cấu trúc Project

```
.
├── app.py                 # Ứng dụng Flask chính
├── csv_storage.py         # Module quản lý user (CSV)
├── file_storage.py        # Module quản lý notes/docs (file)
├── requirements.txt       # Dependencies
├── run.bat / run.sh       # Script chạy nhanh
├── INSTALL.md             # Hướng dẫn cài đặt chi tiết
├── README.md              # Tài liệu này
├── BACKUP_GUIDE.md        # Hướng dẫn backup và restore
├── data/                  # Dữ liệu (QUAN TRỌNG! - Backup thư mục này)
│   ├── users.csv          # Database người dùng (CSV)
│   ├── metadata.json      # Metadata notes/docs
│   ├── edit_logs.json     # Lịch sử chỉnh sửa
│   ├── categories.json    # Danh mục
│   ├── notes/             # Nội dung ghi chú (*.txt)
│   ├── docs/              # Nội dung tài liệu (*.txt)
│   └── uploads/           # File đính kèm
│       ├── notes/         # File đính kèm của ghi chú
│       └── docs/          # File đính kèm của tài liệu
├── templates/            # HTML templates
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

## Lưu ý quan trọng khi chuyển máy

⚠️ **KHI CHUYỂN SANG MÁY KHÁC, NHỚ SAO CHÉP:**

1. ✅ `data/` - **QUAN TRỌNG NHẤT!** Toàn bộ dữ liệu nằm trong đây:
   - `users.csv` - Database người dùng
   - `metadata.json` - Metadata notes/docs
   - `notes/`, `docs/` - Nội dung
   - `uploads/` - File đính kèm
   - `edit_logs.json`, `categories.json` - Cấu hình khác
2. ✅ `templates/` - Templates HTML
3. ✅ `static/` - CSS và JavaScript

**Lưu ý:** Chỉ cần backup thư mục `data/` là đủ cho toàn bộ dữ liệu!

Xem file `BACKUP_GUIDE.md` để biết hướng dẫn backup chi tiết.
Xem file `FILES_TO_COPY.txt` để biết danh sách đầy đủ.

## Lưu ý bảo mật

- Thay đổi `SECRET_KEY` trong `app.py` khi deploy production
- Đổi mật khẩu admin ngay sau lần đăng nhập đầu tiên
- **Backup định kỳ thư mục `data/`** - Tất cả dữ liệu đã được tổ chức trong thư mục này để dễ backup
- Xem `BACKUP_GUIDE.md` để biết hướng dẫn backup chi tiết

## 🚀 Production Deployment

Để deploy lên production server, xem hướng dẫn chi tiết tại:
- **[PRODUCTION_DEPLOY.md](PRODUCTION_DEPLOY.md)** - Hướng dẫn deploy đầy đủ
- **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)** - Tóm tắt các cải tiến

### Quick Deploy (Linux)

```bash
# 1. Clone code
git clone https://github.com/YOUR_USERNAME/internal_management.git
cd internal_management

# 2. Setup
./deploy_production.sh

# 3. Configure
nano .env  # Thay đổi SECRET_KEY

# 4. Run
./run_production.sh
```

### Production Features

- ✅ Gunicorn WSGI server với multi-workers
- ✅ Logging với rotation (10MB, 10 backups)
- ✅ Error handlers (404, 403, 500, 413)
- ✅ Environment-based configuration
- ✅ Systemd service support
- ✅ Nginx reverse proxy ready
- ✅ SSL/HTTPS support
- ✅ Security hardening

## License

MIT License

