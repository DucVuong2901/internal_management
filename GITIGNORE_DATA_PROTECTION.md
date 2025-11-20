# 🔒 Git Ignore: Bảo Vệ Dữ Liệu Người Dùng

## 🎯 Mục Đích

**KHÔNG** push dữ liệu cá nhân và cache lên GitHub:
- ✅ Bảo vệ thông tin người dùng
- ✅ Bảo vệ tin nhắn chat
- ✅ Bảo vệ file đính kèm
- ✅ Bảo vệ thông báo
- ✅ Giữ repo sạch sẽ

## 📁 Files & Folders Được Ignore

### 1. **User Data**
```gitignore
data/users.csv              # Thông tin tài khoản
data/metadata.json          # Metadata notes/docs
data/edit_logs.json         # Lịch sử chỉnh sửa
data/categories.json        # Danh mục
```

### 2. **Notes & Documents**
```gitignore
data/notes/*.txt            # Nội dung notes
data/docs/*.txt             # Nội dung documents
data/uploads/**             # File đính kèm notes/docs
```

### 3. **Chat Data** ⭐ MỚI
```gitignore
data/chat_messages.json     # Tin nhắn chat
data/chat_storage_info.json # Thông tin storage
data/chat_uploads/**        # File đính kèm chat
```

### 4. **Notifications** ⭐ MỚI
```gitignore
data/notifications.json     # Thông báo
```

### 5. **Environment & Logs**
```gitignore
.env                        # Biến môi trường
.env.local
.env.production
*.log                       # Log files
data/logs/
```

### 6. **Python Cache**
```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
```

## 📂 Cấu Trúc Thư Mục

### Được Commit (Cấu trúc):
```
data/
├── .gitkeep
├── notes/
│   └── .gitkeep          ✅ Commit
├── docs/
│   └── .gitkeep          ✅ Commit
├── uploads/
│   ├── .gitkeep          ✅ Commit
│   ├── notes/
│   │   └── .gitkeep      ✅ Commit
│   └── docs/
│       └── .gitkeep      ✅ Commit
└── chat_uploads/
    └── .gitkeep          ✅ Commit (MỚI)
```

### KHÔNG Commit (Dữ liệu):
```
data/
├── users.csv             ❌ Ignore
├── metadata.json         ❌ Ignore
├── categories.json       ❌ Ignore
├── chat_messages.json    ❌ Ignore (MỚI)
├── notifications.json    ❌ Ignore (MỚI)
├── notes/
│   └── *.txt             ❌ Ignore
├── docs/
│   └── *.txt             ❌ Ignore
├── uploads/
│   └── **/*              ❌ Ignore
└── chat_uploads/
    └── **/*              ❌ Ignore (MỚI)
```

## 🔍 Kiểm Tra Files Sẽ Commit

### Trước khi commit:
```bash
# Xem files sẽ được commit
git status

# Xem files bị ignore
git status --ignored
```

### Kiểm tra cụ thể:
```bash
# Kiểm tra file có bị ignore không
git check-ignore -v data/chat_messages.json
git check-ignore -v data/notifications.json
git check-ignore -v data/chat_uploads/image.png
```

### Kết quả mong đợi:
```
✅ .gitignore:70:data/chat_messages.json
✅ .gitignore:76:data/notifications.json
✅ .gitignore:72:data/chat_uploads/**
```

## 🚨 Lưu Ý Quan Trọng

### ⚠️ KHÔNG BAO GIỜ commit:
- ❌ `data/users.csv` - Thông tin đăng nhập
- ❌ `data/chat_messages.json` - Tin nhắn riêng tư
- ❌ `data/chat_uploads/**` - File đính kèm
- ❌ `data/notifications.json` - Thông báo
- ❌ `.env` - API keys, secrets

### ✅ LUÔN commit:
- ✅ `.gitkeep` files - Giữ cấu trúc thư mục
- ✅ Source code (`.py`, `.html`, `.css`, `.js`)
- ✅ Config templates (`.env.example`)
- ✅ Documentation (`.md`)

## 🛡️ Bảo Mật

### Nếu Đã Commit Nhầm:

#### 1. Xóa file khỏi Git (giữ local):
```bash
git rm --cached data/chat_messages.json
git rm --cached data/notifications.json
git rm --cached -r data/chat_uploads/
git commit -m "Remove sensitive data from git"
```

#### 2. Xóa khỏi lịch sử (nếu cần):
```bash
# Cẩn thận! Thao tác này thay đổi lịch sử
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch data/chat_messages.json" \
  --prune-empty --tag-name-filter cat -- --all
```

#### 3. Force push (nếu đã push):
```bash
git push origin --force --all
```

## 📋 Checklist Trước Khi Push

### ✅ Kiểm tra:
```bash
# 1. Xem files sẽ commit
git status

# 2. Đảm bảo không có:
#    - data/users.csv
#    - data/chat_messages.json
#    - data/notifications.json
#    - data/chat_uploads/*
#    - .env

# 3. Chỉ thấy:
#    - Source code
#    - .gitkeep files
#    - Documentation

# 4. Commit
git add .
git commit -m "Your message"

# 5. Push
git push
```

## 🔄 Workflow

### Khi Clone Repo Mới:
```bash
# 1. Clone
git clone <repo-url>
cd internal_management

# 2. Cấu trúc thư mục đã có (từ .gitkeep)
ls data/
# notes/ docs/ uploads/ chat_uploads/

# 3. Tạo file .env
cp .env.example .env
# Edit .env với config của bạn

# 4. Chạy app
python app.py
# App tự tạo các file data cần thiết
```

### Khi Phát Triển:
```bash
# 1. Code bình thường
# 2. Test với dữ liệu thật
# 3. Trước khi commit:
git status
# Đảm bảo không có data files

# 4. Commit chỉ code
git add app.py templates/ static/
git commit -m "Add feature X"
git push
```

## 📊 So Sánh

### Trước:
```
❌ Risk: Có thể commit nhầm data
❌ Privacy: Tin nhắn có thể lộ
❌ Security: File uploads public
```

### Sau:
```
✅ Protected: Data được ignore
✅ Privacy: Tin nhắn an toàn
✅ Security: File uploads private
✅ Clean: Repo chỉ có code
```

## 🎯 Files Được Ignore (Tóm Tắt)

### User Data:
- `data/users.csv`
- `data/metadata.json`
- `data/edit_logs.json`
- `data/categories.json`

### Content:
- `data/notes/*.txt`
- `data/docs/*.txt`
- `data/uploads/**`

### Chat: ⭐
- `data/chat_messages.json`
- `data/chat_storage_info.json`
- `data/chat_uploads/**`

### Notifications: ⭐
- `data/notifications.json`

### System:
- `.env`
- `*.log`
- `__pycache__/`

## 💡 Best Practices

### 1. **Luôn Kiểm Tra**
```bash
git status
```

### 2. **Sử Dụng .env**
```bash
# Không hardcode secrets
SECRET_KEY=your-secret-here  # ❌

# Dùng .env
SECRET_KEY=os.getenv('SECRET_KEY')  # ✅
```

### 3. **Backup Riêng**
```bash
# Backup data ra ngoài repo
tar -czf backup.tar.gz data/
# Lưu backup ở nơi an toàn
```

### 4. **Review Trước Push**
```bash
git diff --cached
# Xem những gì sẽ commit
```

## 🎉 Kết Quả

### Repo Sạch Sẽ:
```
✅ Chỉ có source code
✅ Chỉ có documentation
✅ Chỉ có cấu trúc thư mục
✅ KHÔNG có dữ liệu người dùng
✅ KHÔNG có tin nhắn
✅ KHÔNG có file uploads
✅ KHÔNG có secrets
```

### Bảo Mật:
```
✅ Thông tin cá nhân được bảo vệ
✅ Tin nhắn riêng tư
✅ File đính kèm an toàn
✅ Secrets không bị lộ
```

Bây giờ dữ liệu người dùng **hoàn toàn an toàn** và không bao giờ bị push lên GitHub! 🔒
