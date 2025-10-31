# Hướng dẫn nhanh đưa lên GitHub

**Repository:** https://github.com/DucVuong2901/internal_management.git

## ⚡ Push code tự động (Khuyên dùng)

Chỉ cần chạy script:

**Windows:**
```cmd
push_to_github.bat
```

**Linux/Mac:**
```bash
chmod +x push_to_github.sh
./push_to_github.sh
```

Script sẽ tự động:
- Khởi tạo Git (nếu chưa có)
- Thêm remote origin
- Add tất cả file
- Commit và push lên GitHub

**Lưu ý:** Nếu cần authentication, GitHub sẽ yêu cầu:
- **Username:** DucVuong2901
- **Password:** Personal Access Token (không phải mật khẩu GitHub)
  - Tạo token tại: https://github.com/settings/tokens
  - Quyền: `repo` (full control of private repositories)

## 🔧 Push thủ công

Nếu script không hoạt động, chạy từng lệnh:

```bash
git init
git remote add origin https://github.com/DucVuong2901/internal_management.git
git add .
git commit -m "Initial commit: Hệ thống Quản lý Nội bộ - Support Windows and Linux"
git branch -M main
git push -u origin main
```

## ✅ Xong!

Bây giờ bạn có thể:
- Xem code trên GitHub
- Clone về máy khác: `git clone https://github.com/YOUR_USERNAME/internal_management.git`
- Chia sẻ với người khác

## 📝 Lưu ý

- **Dữ liệu trong `data/` sẽ KHÔNG được commit** (đã cấu hình trong .gitignore)
- Chỉ code được đưa lên GitHub, không có dữ liệu người dùng
- Backup dữ liệu riêng biệt nếu cần

