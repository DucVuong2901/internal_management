# Tính năng Danh mục Con (Sub-categories)

## 📋 Tổng quan

Đã thêm tính năng **danh mục con** (hierarchical categories) vào hệ thống, cho phép tạo cấu trúc danh mục phân cấp.

## ✨ Tính năng mới

### 1. Cấu trúc danh mục phân cấp
- **Danh mục gốc** (root categories): Danh mục chính không có parent
- **Danh mục con** (sub-categories): Danh mục thuộc về một danh mục cha

### 2. Quản lý danh mục
- ✅ Tạo danh mục gốc
- ✅ Tạo danh mục con bằng cách chọn danh mục cha
- ✅ Xóa danh mục con
- ✅ Không thể xóa danh mục cha nếu còn danh mục con
- ✅ Hiển thị số lượng danh mục con

### 3. Sử dụng trong Notes/Docs
- Có thể chọn cả danh mục gốc và danh mục con khi tạo/sửa ghi chú hoặc tài liệu
- Hiển thị đường dẫn đầy đủ: `parent > child`

## 🔧 Thay đổi kỹ thuật

### Cấu trúc dữ liệu

**Trước (list đơn giản):**
```json
[
  "general",
  "công việc",
  "cá nhân"
]
```

**Sau (dictionary với parent-child):**
```json
{
  "general": {
    "name": "general",
    "parent": null,
    "children": []
  },
  "công việc": {
    "name": "công việc",
    "parent": null,
    "children": ["dự án a", "dự án b"]
  },
  "dự án a": {
    "name": "dự án a",
    "parent": "công việc",
    "children": []
  }
}
```

### Functions mới trong app.py

```python
# Lấy đường dẫn đầy đủ của category
get_category_full_path(category_name)
# Ví dụ: "công việc > dự án a"

# Lấy tất cả tên categories (backward compatibility)
get_all_category_names(categories=None)
# Returns: ['general', 'công việc', 'dự án a', ...]

# Lấy danh sách categories gốc
get_root_categories(categories=None)

# Lấy danh sách categories con của một parent
get_child_categories(parent_name, categories=None)
```

### Routes đã cập nhật

**`/admin/categories/add` (POST)**
- Thêm parameter `parent` để chỉ định danh mục cha
- Tự động cập nhật `children` của parent

**`/admin/categories/delete` (POST)**
- Kiểm tra có danh mục con không trước khi xóa
- Tự động xóa khỏi `children` của parent

## 📖 Hướng dẫn sử dụng

### Tạo danh mục gốc

1. Vào **Admin > Quản lý Danh mục**
2. Nhập tên danh mục
3. Để trống "Danh mục cha"
4. Click "Thêm danh mục"

### Tạo danh mục con

1. Vào **Admin > Quản lý Danh mục**
2. Nhập tên danh mục con
3. Chọn danh mục cha từ dropdown
4. Click "Thêm danh mục"

**Ví dụ:**
- Danh mục cha: `công việc`
- Danh mục con: `dự án a`, `dự án b`, `meeting`

### Xóa danh mục

**Xóa danh mục con:**
- Click nút "Xóa" bên cạnh danh mục con
- Confirm xóa

**Xóa danh mục cha:**
- Phải xóa tất cả danh mục con trước
- Nút "Xóa" sẽ bị disable nếu còn danh mục con

### Sử dụng khi tạo Note/Doc

1. Khi tạo hoặc sửa ghi chú/tài liệu
2. Chọn danh mục từ dropdown
3. Có thể chọn cả danh mục gốc và danh mục con
4. Hệ thống sẽ hiển thị đường dẫn đầy đủ (nếu là danh mục con)

## 🔄 Backward Compatibility

✅ **Hoàn toàn tương thích ngược:**
- File `categories.json` cũ (dạng list) sẽ tự động convert sang cấu trúc mới
- Dữ liệu notes/docs hiện tại không bị ảnh hưởng
- Các category cũ sẽ trở thành danh mục gốc

**Migration tự động:**
```python
# Khi load categories, nếu phát hiện format cũ (list):
if isinstance(data, list):
    new_data = {}
    for cat in data:
        new_data[cat] = {'name': cat, 'parent': None, 'children': []}
    save_categories(new_data)
```

## 🎨 UI Changes

### Trang Quản lý Danh mục

**Trước:**
- Danh sách phẳng các danh mục
- Chỉ có nút Xóa

**Sau:**
- Hiển thị cấu trúc phân cấp
- Danh mục gốc với icon folder 📁
- Danh mục con thụt vào với icon tag 🏷️
- Badge hiển thị số lượng danh mục con
- Nút Xóa disabled nếu còn danh mục con

### Form Tạo/Sửa Note/Doc

**Thêm:**
- Dropdown chọn danh mục cha (khi tạo danh mục mới)
- Hiển thị đường dẫn đầy đủ trong dropdown

## 📝 Ví dụ sử dụng

### Cấu trúc danh mục đề xuất

```
📁 công việc
  └─ 🏷️ dự án a
  └─ 🏷️ dự án b
  └─ 🏷️ meeting

📁 cá nhân
  └─ 🏷️ sức khỏe
  └─ 🏷️ tài chính
  └─ 🏷️ gia đình

📁 học tập
  └─ 🏷️ python
  └─ 🏷️ javascript
  └─ 🏷️ database

📁 general (mặc định)
```

### Use cases

**1. Quản lý dự án:**
```
công việc
  ├─ dự án website
  ├─ dự án mobile app
  └─ dự án api
```

**2. Quản lý kiến thức:**
```
học tập
  ├─ lập trình
  │   ├─ python
  │   └─ javascript
  └─ database
      ├─ mysql
      └─ mongodb
```

**Lưu ý:** Hiện tại chỉ hỗ trợ 2 cấp (parent > child). Nếu cần nhiều cấp hơn, có thể mở rộng sau.

## 🐛 Lưu ý

1. **Không thể xóa danh mục cha nếu còn danh mục con**
   - Phải xóa danh mục con trước
   - Hoặc di chuyển danh mục con sang parent khác (feature tương lai)

2. **Danh mục "general" không thể xóa**
   - Đây là danh mục mặc định
   - Không thể làm danh mục con

3. **Tên danh mục tự động lowercase**
   - Để tránh trùng lặp do chữ hoa/thường

## 🔮 Tính năng tương lai (có thể mở rộng)

- [ ] Di chuyển danh mục con sang parent khác
- [ ] Hỗ trợ nhiều cấp (parent > child > grandchild)
- [ ] Sắp xếp thứ tự danh mục
- [ ] Icon tùy chỉnh cho mỗi danh mục
- [ ] Màu sắc cho danh mục
- [ ] Filter notes theo danh mục con
- [ ] Thống kê số lượng notes trong mỗi danh mục con

## ✅ Testing Checklist

- [x] Tạo danh mục gốc
- [x] Tạo danh mục con
- [x] Xóa danh mục con
- [x] Không cho xóa danh mục cha khi còn con
- [x] Backward compatibility với categories.json cũ
- [ ] Tạo note với danh mục con
- [ ] Sửa note đổi sang danh mục con
- [ ] Hiển thị đường dẫn đầy đủ trong UI
- [ ] Filter notes theo danh mục con

---

**Tóm lại**: Tính năng danh mục con đã được implement với backward compatibility đầy đủ. Hệ thống cũ vẫn hoạt động bình thường và tự động migrate sang cấu trúc mới.
