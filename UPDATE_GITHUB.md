# Hướng dẫn Update Code lên GitHub

## 🚀 Cách nhanh nhất (Windows)

### Option 1: Dùng script tự động (Khuyên dùng)

**Chạy file batch:**
```bash
# Cách 1: Double-click vào file
QUICK_PUSH.bat

# Cách 2: Hoặc chạy từ Command Prompt
cd D:\internal_management
QUICK_PUSH.bat
```

**Hoặc dùng PowerShell:**
```powershell
cd D:\internal_management
.\auto_push.ps1
```

---

## 📝 Cách thủ công (nếu script không hoạt động)

Mở Command Prompt hoặc PowerShell trong thư mục dự án:

```bash
# 1. Di chuyển vào thư mục dự án
cd D:\internal_management

# 2. Kiểm tra trạng thái thay đổi
git status

# 3. Thêm tất cả file đã thay đổi
git add .

# 4. Commit với message mô tả
git commit -m "Add export/import data feature for admin"

# 5. Push lên GitHub
git push origin main
```

---

## 🔄 Các tình huống thường gặp

### Nếu lần đầu tiên push:
```bash
# Kiểm tra remote đã được set chưa
git remote -v

# Nếu chưa có, thêm remote:
git remote add origin https://github.com/DucVuong2901/internal_management.git

# Set branch main
git branch -M main

# Push lần đầu
git push -u origin main
```

### Nếu có lỗi "Repository đã có code khác":
```bash
# Pull code từ GitHub trước
git pull origin main --allow-unrelated-histories

# Sau đó push lại
git push origin main
```

### Nếu cần xác thực:
- **Username:** `DucVuong2901`
- **Password:** Personal Access Token (không phải mật khẩu GitHub)
  - Tạo token tại: https://github.com/settings/tokens
  - Quyền: chọn `repo` (Full control of private repositories)

---

## 💡 Lệnh Git thường dùng

```bash
# Xem trạng thái file đã thay đổi
git status

# Xem lịch sử commit
git log --oneline

# Xem thay đổi chi tiết
git diff

# Thêm file cụ thể
git add app.py templates/export_import.html

# Commit với message mô tả
git commit -m "Thêm chức năng export/import dữ liệu"

# Push lên GitHub
git push

# Pull code mới từ GitHub
git pull
```

---

## ⚠️ Lưu ý quan trọng

1. **Kiểm tra file trước khi commit:**
   - Không commit file trong thư mục `data/` (đã có trong `.gitignore`)
   - Không commit file nhạy cảm như password, API keys

2. **Commit message rõ ràng:**
   - Mô tả ngắn gọn những gì đã thay đổi
   - Ví dụ: "Add export/import feature", "Fix import bug", "Update templates"

3. **Pull trước khi push:**
   - Nếu làm việc trên nhiều máy, luôn `git pull` trước khi `git push`

---

## 🎯 Quick Reference

**Update code mới lên GitHub:**
```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

**Xem code trên GitHub:**
https://github.com/DucVuong2901/internal_management

---

## 🆘 Nếu gặp lỗi

1. **Lỗi authentication:**
   - Tạo Personal Access Token tại GitHub Settings
   - Dùng token làm password khi push

2. **Lỗi conflict:**
   ```bash
   git pull origin main
   # Giải quyết conflict nếu có
   git add .
   git commit -m "Resolve conflicts"
   git push
   ```

3. **Lỗi "not a git repository":**
   ```bash
   git init
   git remote add origin https://github.com/DucVuong2901/internal_management.git
   ```

---

**Tóm lại:** Chạy `QUICK_PUSH.bat` là cách nhanh nhất! 🚀

