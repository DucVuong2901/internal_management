# 🚀 Hướng dẫn Migration: CSV/JSON → Database

## 📋 Tổng quan

Migration này chuyển đổi hệ thống lưu trữ từ **CSV/JSON files** sang **SQLite Database** mà **KHÔNG MẤT DỮ LIỆU CŨ**.

### ✅ Lợi ích của Database

- **Performance tốt hơn** - Query nhanh hơn với index
- **ACID compliance** - Đảm bảo tính toàn vẹn dữ liệu
- **Relationships** - Foreign keys, joins
- **Scalability** - Dễ scale lên PostgreSQL/MySQL
- **Backup dễ dàng** - 1 file database.db
- **Concurrent access** - Xử lý đồng thời tốt hơn

## 🔧 Cài đặt

### 1. Install dependencies

```bash
pip install flask-sqlalchemy
```

### 2. Backup dữ liệu cũ (QUAN TRỌNG!)

```bash
# Windows
xcopy data data_backup /E /I /H

# Linux/Mac
cp -r data data_backup
```

## 🚀 Chạy Migration

### Bước 1: Chạy migration script

```bash
python migrate_to_database.py
```

Script sẽ:
- ✅ Tạo database schema
- ✅ Copy users từ CSV
- ✅ Copy categories từ JSON
- ✅ Copy notes từ files + metadata
- ✅ Copy documents từ files + metadata
- ✅ Copy edit logs từ JSON
- ✅ **KHÔNG XÓA** dữ liệu cũ

### Bước 2: Kiểm tra dữ liệu

```bash
# Mở SQLite database
sqlite3 data/database.db

# Check tables
.tables

# Check users
SELECT * FROM users;

# Check notes count
SELECT COUNT(*) FROM notes;

# Exit
.exit
```

### Bước 3: Test application

```bash
# Chạy app với database
python app.py
```

Kiểm tra:
- ✅ Đăng nhập
- ✅ Xem notes/docs
- ✅ Tạo mới notes/docs
- ✅ Edit/Delete
- ✅ Categories
- ✅ Attachments

## 📊 Cấu trúc Database

### Tables

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── password_hash
├── role
├── is_active
├── created_at
└── updated_at

categories
├── id (PK)
├── key (unique) - "parent/child" hoặc "category"
├── name
├── display_name
├── parent_key (FK)
└── created_at

notes
├── id (PK)
├── title
├── content
├── category_key (FK)
├── user_id (FK)
├── updated_by (FK)
├── view_count
├── created_at
└── updated_at

documents
├── id (PK)
├── title
├── content
├── category_key (FK)
├── user_id (FK)
├── updated_by (FK)
├── created_at
└── updated_at

attachments
├── id (PK)
├── filename
├── original_filename
├── file_type ('note' or 'doc')
├── note_id (FK)
├── document_id (FK)
└── uploaded_at

edit_logs
├── id (PK)
├── item_type
├── item_id
├── action
├── user_id (FK)
├── changes (JSON)
└── timestamp
```

## 🔄 Rollback (nếu cần)

Nếu có vấn đề, rollback về CSV/JSON:

```bash
# 1. Xóa database
rm data/database.db

# 2. Restore backup (nếu có)
# Windows
xcopy data_backup data /E /I /H /Y

# Linux/Mac
cp -r data_backup/* data/

# 3. Comment out database code trong app.py
# 4. Uncomment CSV/JSON storage code
```

## 📝 Sau khi Migration

### Cập nhật app.py

```python
# TRƯỚC (CSV/JSON):
from csv_storage import CSVUserStorage
from file_storage import FileStorage

user_storage = CSVUserStorage(...)
file_storage = FileStorage(...)

# SAU (Database):
from models import db, User, Note, Document, Category
from db_storage import DatabaseUserStorage, DatabaseFileStorage

db.init_app(app)
user_storage = DatabaseUserStorage(db)
file_storage = DatabaseFileStorage(db)
```

### Giữ lại CSV/JSON files

**KHÔNG XÓA** các files cũ:
- `data/users.csv` - Backup users
- `data/metadata.json` - Backup metadata
- `data/categories.json` - Backup categories
- `data/notes/*.txt` - Backup note content
- `data/docs/*.txt` - Backup document content

Lý do:
- ✅ Backup an toàn
- ✅ Có thể rollback
- ✅ Audit trail
- ✅ Data recovery

## 🔍 Troubleshooting

### Lỗi: "Table already exists"

```bash
# Xóa database và chạy lại
rm data/database.db
python migrate_to_database.py
```

### Lỗi: "Foreign key constraint failed"

Nguyên nhân: Category không tồn tại

Giải pháp:
```python
# Trong migrate_to_database.py
# Đảm bảo migrate_categories() chạy TRƯỚC migrate_notes()
```

### Lỗi: "File not found"

Nguyên nhân: Note/Doc file bị mất

Giải pháp:
- Script sẽ skip và báo warning
- Kiểm tra `data/notes/` và `data/docs/`

## 📈 Performance

### Indexes

Database tự động tạo indexes cho:
- `users.username`
- `categories.key`
- `notes.category_key`
- `notes.created_at`
- `documents.category_key`
- `edit_logs.item_type`
- `edit_logs.timestamp`

### Query optimization

```python
# Eager loading để tránh N+1 queries
notes = Note.query.options(
    db.joinedload(Note.category),
    db.joinedload(Note.author)
).all()
```

## 🎯 Next Steps

1. ✅ Chạy migration
2. ✅ Test kỹ
3. ✅ Deploy lên production
4. ✅ Monitor performance
5. ✅ Backup database định kỳ

## 💾 Backup Database

### Manual backup

```bash
# Backup
cp data/database.db data/database_backup_$(date +%Y%m%d).db

# Restore
cp data/database_backup_20250108.db data/database.db
```

### Automated backup (cron)

```bash
# Linux crontab
0 2 * * * cp /path/to/data/database.db /path/to/backup/database_$(date +\%Y\%m\%d).db
```

## 🚀 Scale lên PostgreSQL (tương lai)

Khi cần scale:

```python
# config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/dbname'
```

Migration tự động với Alembic:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## ✅ Checklist

- [ ] Backup dữ liệu cũ
- [ ] Install flask-sqlalchemy
- [ ] Chạy migrate_to_database.py
- [ ] Kiểm tra database
- [ ] Test application
- [ ] Deploy
- [ ] Monitor
- [ ] Setup backup tự động

## 📞 Support

Nếu gặp vấn đề:
1. Check logs trong console
2. Kiểm tra data/database.db có tồn tại không
3. Rollback về CSV/JSON nếu cần
4. Contact admin

---

**LƯU Ý:** Migration này an toàn và có thể rollback. Dữ liệu cũ không bị xóa!
