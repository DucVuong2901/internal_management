# Hướng dẫn Backup và Restore

## Cấu trúc dữ liệu

Tất cả dữ liệu của hệ thống được lưu trong thư mục `data/` để dễ dàng backup và quản lý.

### Cấu trúc thư mục data/

```
data/
├── users.csv              # Danh sách người dùng và quyền truy cập
├── metadata.json          # Metadata của notes và documents
├── edit_logs.json         # Lịch sử chỉnh sửa
├── categories.json        # Danh mục phân loại
├── notes/                 # Nội dung các ghi chú
│   ├── 1.txt
│   ├── 2.txt
│   └── ...
├── docs/                  # Nội dung các tài liệu
│   ├── 1.txt
│   ├── 2.txt
│   └── ...
└── uploads/               # File đính kèm
    ├── notes/             # File đính kèm của ghi chú
    └── docs/              # File đính kèm của tài liệu
```

## Backup dữ liệu

### Phương pháp 1: Backup toàn bộ thư mục data (Khuyến nghị)

Đơn giản nhất, chỉ cần copy toàn bộ thư mục `data/`:

**Windows:**
```batch
xcopy /E /I data backup_data_20240101
```

**Linux/Mac:**
```bash
cp -r data backup_data_20240101
```

### Phương pháp 2: Backup bằng ZIP

**Windows:**
```batch
powershell Compress-Archive -Path data -DestinationPath backup_data_20240101.zip
```

**Linux/Mac:**
```bash
zip -r backup_data_20240101.zip data/
```

### Phương pháp 3: Backup tự động (Script)

Tạo file `backup.bat` (Windows) hoặc `backup.sh` (Linux/Mac):

**Windows (backup.bat):**
```batch
@echo off
set BACKUP_DIR=backups
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
set TIME=%time:~0,2%%time:~3,2%%time:~6,2%
set TIME=%TIME: =0%
set FILENAME=backup_%DATE%_%TIME%.zip

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%
powershell Compress-Archive -Path data -DestinationPath %BACKUP_DIR%\%FILENAME%
echo Backup hoan thanh: %BACKUP_DIR%\%FILENAME%
```

**Linux/Mac (backup.sh):**
```bash
#!/bin/bash
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="backup_${DATE}.zip"

mkdir -p $BACKUP_DIR
zip -r $BACKUP_DIR/$FILENAME data/
echo "Backup hoàn thành: $BACKUP_DIR/$FILENAME"
```

## Restore dữ liệu

### Cách 1: Restore từ thư mục backup

1. Dừng ứng dụng (nếu đang chạy)
2. Backup thư mục `data/` hiện tại (đề phòng)
3. Copy thư mục backup thay thế thư mục `data/` hiện tại
4. Khởi động lại ứng dụng

### Cách 2: Restore từ file ZIP

1. Dừng ứng dụng (nếu đang chạy)
2. Backup thư mục `data/` hiện tại
3. Xóa hoặc đổi tên thư mục `data/` cũ
4. Giải nén file backup ZIP
5. Đảm bảo thư mục `data/` được tạo đúng cách
6. Khởi động lại ứng dụng

## Backup tự động định kỳ

### Windows Task Scheduler

1. Tạo task mới trong Task Scheduler
2. Trỏ đến script `backup.bat`
3. Thiết lập chạy hàng ngày/giờ

### Linux Cron

Thêm vào crontab (`crontab -e`):
```cron
# Backup hàng ngày lúc 2:00 AM
0 2 * * * /path/to/backup.sh
```

## Lưu ý quan trọng

1. **Luôn backup trước khi cập nhật:** Trước khi nâng cấp hoặc thay đổi hệ thống, luôn backup dữ liệu
2. **Kiểm tra backup:** Sau khi backup, nên kiểm tra file có đầy đủ không
3. **Lưu nhiều bản backup:** Giữ lại nhiều bản backup từ các thời điểm khác nhau
4. **Backup offline:** Tốt nhất là backup khi ứng dụng không chạy để tránh dữ liệu không đồng bộ
5. **Mã hóa backup nhạy cảm:** Nếu dữ liệu nhạy cảm, nên mã hóa file backup

## File quan trọng cần backup

- ✅ `data/users.csv` - Quan trọng nhất, chứa thông tin người dùng
- ✅ `data/metadata.json` - Metadata của tất cả notes và docs
- ✅ `data/notes/` - Toàn bộ nội dung ghi chú
- ✅ `data/docs/` - Toàn bộ nội dung tài liệu
- ✅ `data/uploads/` - File đính kèm
- ✅ `data/edit_logs.json` - Lịch sử chỉnh sửa (tùy chọn)
- ✅ `data/categories.json` - Danh mục phân loại (tùy chọn)

## Di chuyển sang server khác

Để di chuyển toàn bộ hệ thống sang server khác:

1. Backup thư mục `data/` (theo hướng dẫn trên)
2. Copy code ứng dụng và các file cấu hình
3. Cài đặt dependencies: `pip install -r requirements.txt`
4. Copy thư mục `data/` vào vị trí đúng
5. Chạy ứng dụng: `python app.py`

Đảm bảo quyền truy cập file (Linux/Mac) và đường dẫn đúng.

