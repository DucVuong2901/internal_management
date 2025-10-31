# Checklist chuẩn bị đưa lên GitHub

## ✅ Trước khi push

- [x] Đã cấu hình `.gitignore` để loại trừ dữ liệu nhạy cảm
- [x] Đã tạo các file `.gitkeep` để giữ cấu trúc thư mục
- [x] Đã cập nhật `README.md` với hướng dẫn GitHub
- [x] Đã tạo các script hỗ trợ: `setup_git.bat`, `setup_git.sh`
- [x] Đã có file `GITHUB_SETUP.md` và `GIT_QUICKSTART.md`

## ⚠️ Kiểm tra bảo mật

Trước khi commit, hãy kiểm tra:

- [ ] Đổi `SECRET_KEY` trong `app.py` (dòng 20) trước khi push
- [ ] Đảm bảo không có mật khẩu hardcode trong code
- [ ] Kiểm tra `.gitignore` đã loại trừ đúng các file nhạy cảm

**Mặc định SECRET_KEY:** `'your-secret-key-change-this'` - **CẦN ĐỔI** trước khi push!

## 📦 Files sẽ được commit

✅ Code Python (.py files)
✅ Templates HTML
✅ Static files (CSS, JS)
✅ Configuration files (.md, .txt, .sh, .bat)
✅ Scripts chạy ứng dụng
✅ `.gitignore`
✅ File hướng dẫn

## 🚫 Files sẽ KHÔNG được commit

❌ `data/users.csv` - Dữ liệu người dùng
❌ `data/metadata.json` - Metadata
❌ `data/notes/*.txt` - Nội dung ghi chú
❌ `data/docs/*.txt` - Nội dung tài liệu
❌ `data/uploads/**` - File đính kèm
❌ `__pycache__/` - Python cache
❌ `instance/` - Flask instance folder
❌ `.vscode/`, `.idea/` - IDE settings

## 🚀 Các bước thực hiện

1. **Kiểm tra lại .gitignore:**
   ```bash
   git status
   ```
   Đảm bảo các file trong `data/` không xuất hiện

2. **Khởi tạo Git (nếu chưa):**
   ```bash
   git init
   ```

3. **Add và commit:**
   ```bash
   git add .
   git commit -m "Initial commit: Hệ thống Quản lý Nội bộ"
   ```

4. **Tạo repository trên GitHub và push:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/internal_management.git
   git branch -M main
   git push -u origin main
   ```

## 🔄 Cập nhật sau khi push

Để cập nhật code sau khi đã push:
```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

