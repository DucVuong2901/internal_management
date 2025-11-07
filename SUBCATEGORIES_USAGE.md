# Hướng dẫn sử dụng Danh mục Con

## ✨ Tính năng mới: Danh mục Con (Hierarchical Categories)

Hệ thống giờ đây hỗ trợ **danh mục con** - cho phép tạo cấu trúc danh mục phân cấp 2 cấp (parent > child).

## 📖 Cách sử dụng

### 1. Tạo danh mục gốc (Parent Category)

1. Đăng nhập với tài khoản **Admin**
2. Vào **Admin > Quản lý Danh mục**
3. Nhập tên danh mục (ví dụ: "công việc")
4. **Để trống** dropdown "Danh mục cha"
5. Click **"Thêm danh mục"**

**Kết quả:**
```
📁 công việc
```

### 2. Tạo danh mục con (Sub-category)

1. Vào **Admin > Quản lý Danh mục**
2. Nhập tên danh mục con (ví dụ: "dự án a")
3. **Chọn danh mục cha** từ dropdown (ví dụ: "công việc")
4. Click **"Thêm danh mục"**

**Kết quả:**
```
📁 công việc (1 danh mục con)
  └─ 🏷️ dự án a [Xóa]
```

### 3. Sử dụng khi tạo Ghi chú/Tài liệu

Khi tạo hoặc sửa ghi chú/tài liệu, dropdown danh mục sẽ hiển thị:

```
📁 general
📁 công việc
    └─ dự án a
    └─ dự án b
📁 cá nhân
    └─ sức khỏe
    └─ tài chính
```

**Chọn danh mục:**
- Có thể chọn danh mục gốc (📁 công việc)
- Hoặc chọn danh mục con (└─ dự án a)

### 4. Xóa danh mục

**Xóa danh mục con:**
- Click nút **[Xóa]** bên cạnh danh mục con
- Confirm xóa
- ✅ Xóa thành công

**Xóa danh mục cha:**
- ⚠️ **Không thể xóa** nếu còn danh mục con
- Nút **[Xóa]** sẽ bị **disabled** (màu xám)
- Phải xóa tất cả danh mục con trước

## 💡 Ví dụ thực tế

### Ví dụ 1: Quản lý Dự án

```
📁 công việc
  └─ dự án website
  └─ dự án mobile app
  └─ dự án api
  └─ meeting
```

**Cách tạo:**
1. Tạo danh mục gốc: "công việc"
2. Tạo danh mục con: "dự án website" (parent: công việc)
3. Tạo danh mục con: "dự án mobile app" (parent: công việc)
4. Tạo danh mục con: "dự án api" (parent: công việc)
5. Tạo danh mục con: "meeting" (parent: công việc)

**Sử dụng:**
- Ghi chú về dự án website → Chọn "└─ dự án website"
- Ghi chú meeting chung → Chọn "└─ meeting"
- Ghi chú công việc chung → Chọn "📁 công việc"

### Ví dụ 2: Quản lý Kiến thức

```
📁 học tập
  └─ python
  └─ javascript
  └─ database
  └─ devops
```

**Sử dụng:**
- Ghi chú về Python → Chọn "└─ python"
- Ghi chú về Database → Chọn "└─ database"
- Ghi chú học tập chung → Chọn "📁 học tập"

### Ví dụ 3: Quản lý Cá nhân

```
📁 cá nhân
  └─ sức khỏe
  └─ tài chính
  └─ gia đình
  └─ sở thích
```

## 🎯 Lợi ích

### 1. Tổ chức tốt hơn
- Phân loại chi tiết hơn
- Dễ tìm kiếm
- Cấu trúc rõ ràng

### 2. Linh hoạt
- Có thể chọn danh mục gốc (cho ghi chú chung)
- Hoặc chọn danh mục con (cho ghi chú cụ thể)

### 3. Dễ quản lý
- Nhìn thấy cấu trúc phân cấp ngay trong dropdown
- Icon khác nhau: 📁 (gốc) vs └─ (con)
- Badge hiển thị số danh mục con

## ⚠️ Lưu ý quan trọng

### 1. Không thể xóa danh mục cha nếu còn con
```
📁 công việc (2 danh mục con)  [Xóa] ← Disabled
  └─ dự án a [Xóa] ← Có thể xóa
  └─ dự án b [Xóa] ← Có thể xóa
```

**Giải pháp:** Xóa tất cả danh mục con trước

### 2. Danh mục "general" không thể xóa
- Đây là danh mục mặc định
- Luôn tồn tại trong hệ thống

### 3. Tên danh mục tự động lowercase
- "Dự Án A" → "dự án a"
- Để tránh trùng lặp do chữ hoa/thường

### 4. Chỉ hỗ trợ 2 cấp
- Danh mục gốc (parent)
- Danh mục con (child)
- Không hỗ trợ: grandchild (con của con)

## 🔄 Backward Compatibility

✅ **Hoàn toàn tương thích với dữ liệu cũ:**

**File categories.json cũ (dạng list):**
```json
["general", "công việc", "cá nhân"]
```

**Tự động convert sang:**
```json
{
  "general": {"name": "general", "parent": null, "children": []},
  "công việc": {"name": "công việc", "parent": null, "children": []},
  "cá nhân": {"name": "cá nhân", "parent": null, "children": []}
}
```

**Kết quả:**
- Tất cả danh mục cũ trở thành danh mục gốc
- Không mất dữ liệu
- Ghi chú/tài liệu cũ vẫn hoạt động bình thường

## 📱 Giao diện

### Trang Quản lý Danh mục

**Trước:**
```
general [Xóa]
công việc [Xóa]
cá nhân [Xóa]
```

**Sau:**
```
📁 general (Mặc định)
   Không thể xóa

📁 công việc (2 danh mục con) [Xóa - Disabled]
  └─ 🏷️ dự án a [Xóa]
  └─ 🏷️ dự án b [Xóa]

📁 cá nhân [Xóa]
```

### Dropdown khi tạo Ghi chú

**Trước:**
```
general
công việc
cá nhân
```

**Sau:**
```
📁 general
📁 công việc
    └─ dự án a
    └─ dự án b
📁 cá nhân
```

## 🚀 Tips & Tricks

### 1. Đặt tên danh mục con rõ ràng
❌ Không tốt:
```
📁 công việc
  └─ a
  └─ b
```

✅ Tốt:
```
📁 công việc
  └─ dự án website
  └─ dự án mobile
```

### 2. Không tạo quá nhiều danh mục con
❌ Quá nhiều:
```
📁 công việc (15 danh mục con)
  └─ dự án 1
  └─ dự án 2
  ...
  └─ dự án 15
```

✅ Vừa phải:
```
📁 công việc (4-5 danh mục con)
  └─ dự án active
  └─ dự án archive
  └─ meeting
  └─ planning
```

### 3. Sử dụng danh mục gốc cho ghi chú chung
- Ghi chú chung về công việc → Chọn "📁 công việc"
- Ghi chú cụ thể về dự án → Chọn "└─ dự án a"

## ❓ FAQ

**Q: Có thể tạo danh mục con của danh mục con không?**
A: Không. Hiện tại chỉ hỗ trợ 2 cấp (parent > child).

**Q: Có thể di chuyển danh mục con sang parent khác không?**
A: Chưa hỗ trợ. Cần xóa và tạo lại.

**Q: Xóa danh mục cha thì danh mục con sao?**
A: Không thể xóa danh mục cha nếu còn danh mục con. Phải xóa con trước.

**Q: Xóa danh mục thì ghi chú thuộc danh mục đó sao?**
A: Ghi chú sẽ tự động chuyển về danh mục "general".

**Q: Có thể đổi tên danh mục không?**
A: Chưa hỗ trợ. Cần xóa và tạo lại với tên mới.

---

**Chúc bạn sử dụng tính năng mới hiệu quả!** 🎉
