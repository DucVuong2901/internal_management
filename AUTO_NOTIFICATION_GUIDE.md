# Hướng Dẫn Thông Báo Tự Động

## Tổng Quan

Hệ thống đã được tích hợp để **tự động tạo thông báo** khi có Note hoặc Document mới. Tất cả người dùng sẽ nhận được thông báo với thông tin tóm tắt.

## Cách Hoạt Động

### 1. **Khi Tạo Note Mới**

Khi ai đó tạo note mới, hệ thống sẽ:
- ✅ Tự động tạo thông báo broadcast (gửi cho tất cả)
- ✅ Hiển thị thông tin:
  - 📝 Tiêu đề note
  - 👤 Người tạo
  - 📁 Danh mục
  - 📄 Tóm tắt nội dung (100 ký tự đầu)
- ✅ Link trực tiếp đến note
- ✅ Gửi real-time qua Socket.IO

**Ví dụ thông báo:**
```
📝 Note mới: Hướng dẫn sử dụng hệ thống
Người tạo: admin
Danh mục: Hướng dẫn

Đây là hướng dẫn chi tiết về cách sử dụng hệ thống quản lý nội bộ. Bạn có thể tạo note, document...
```

### 2. **Khi Tạo Document Mới**

Tương tự với note, khi tạo document mới:
- ✅ Thông báo loại "success" (màu xanh lá)
- ✅ Icon 📄 để phân biệt với note
- ✅ Thông tin đầy đủ về document
- ✅ Link trực tiếp đến document

**Ví dụ thông báo:**
```
📄 Tài liệu mới: Quy trình làm việc
Người tạo: admin
Danh mục: Quy trình

Tài liệu này mô tả quy trình làm việc chuẩn của công ty, bao gồm các bước từ lúc nhận việc...
```

## Trải Nghiệm Người Dùng

### Khi Đăng Nhập
1. User đăng nhập vào hệ thống
2. Vào trang **Chat** (hoặc bất kỳ trang nào)
3. Thấy **Notification Panel** bên trái (nếu ở trang Chat)
4. Badge đỏ hiển thị số thông báo chưa đọc

### Xem Thông Báo
1. Click vào thông báo
2. Tự động đánh dấu đã đọc
3. Chuyển hướng đến note/document tương ứng
4. Đọc nội dung đầy đủ

### Real-time Updates
- Khi có note/document mới, **không cần refresh**
- Thông báo xuất hiện ngay lập tức
- Toast notification hiển thị ở góc phải màn hình
- Badge cập nhật số lượng chưa đọc

## Cấu Hình

### Tùy Chỉnh Độ Dài Tóm Tắt

Mặc định: **100 ký tự**

Để thay đổi, chỉnh sửa trong `app.py`:

```python
# Trong route /notes/new
content_summary = content_text[:150] + '...' if len(content_text) > 150 else content_text

# Trong route /docs/new
content_summary = content_text[:150] + '...' if len(content_text) > 150 else content_text
```

### Tùy Chỉnh Loại Thông Báo

**Note mới:**
```python
type="info"  # Màu xanh dương
```

**Document mới:**
```python
type="success"  # Màu xanh lá
```

Có thể đổi thành:
- `"warning"` - Màu vàng
- `"danger"` - Màu đỏ

### Gửi Cho User Cụ Thể

Nếu muốn chỉ gửi cho admin thay vì broadcast:

```python
# Lấy admin user
admin_users = [u for u in user_storage.get_all_users() if u['role'] == 'admin']
if admin_users:
    admin_id = admin_users[0]['id']
    
    notification = notification_storage.create_notification(
        title=f"📝 Note mới: {title}",
        message=f"...",
        type="info",
        user_id=admin_id,  # Chỉ admin nhìn thấy
        link=f"/notes/{note.id}/view"
    )
```

## Kiểm Tra Hoạt Động

### Test Thủ Công

1. **Tạo Note Mới:**
   ```
   1. Đăng nhập với user A
   2. Tạo note mới
   3. Đăng nhập với user B (tab khác)
   4. Vào trang Chat
   5. Kiểm tra notification panel bên trái
   6. Xem thông báo về note mới
   ```

2. **Test Real-time:**
   ```
   1. User A và User B cùng online
   2. User B mở trang Chat
   3. User A tạo note mới
   4. User B thấy toast notification ngay lập tức
   5. Badge cập nhật số lượng chưa đọc
   ```

### Kiểm Tra Database

```python
# Chạy script kiểm tra
python -c "
from notification_storage import NotificationStorage
import os

storage = NotificationStorage(data_dir='data')
notifications = storage.get_notifications(limit=10)

print(f'Tổng số thông báo: {len(notifications)}')
for n in notifications:
    print(f'- [{n[\"type\"]}] {n[\"title\"]}')
"
```

## Troubleshooting

### Không Nhận Được Thông Báo?

**Kiểm tra:**
1. File `data/notifications.json` có tồn tại?
2. Socket.IO có hoạt động? (xem console log)
3. User có đang ở trang Chat? (notification panel chỉ hiện ở đó)

**Debug:**
```python
# Thêm log trong app.py
app.logger.info(f"Created notification: {notification}")
```

### Thông Báo Bị Trùng?

Nếu tạo note nhiều lần và thấy thông báo trùng:
- Đây là hành vi bình thường
- Mỗi lần tạo note = 1 thông báo mới
- Có thể dọn dẹp bằng cách xóa thông báo cũ

### Tóm Tắt Không Hiển Thị Đúng?

Nếu tóm tắt có HTML tags:
```python
# Đảm bảo đã loại bỏ HTML
content_text = re.sub(r'<[^>]+>', '', content)
```

Nếu tóm tắt quá dài:
```python
# Giảm số ký tự
content_summary = content_text[:50] + '...'
```

## Mở Rộng

### Thêm Thông Báo Cho Sự Kiện Khác

**Ví dụ: Thông báo khi note được chỉnh sửa**

```python
# Trong route /notes/<id>/edit
if success:
    # ... existing code ...
    
    # Tạo thông báo cho người tạo note gốc
    if note.user_id and note.user_id != current_user.id:
        notification_storage.create_notification(
            title=f"✏️ Note của bạn được chỉnh sửa",
            message=f"{current_user.username} đã chỉnh sửa note: {title}",
            type="info",
            user_id=note.user_id,  # Chỉ gửi cho người tạo
            link=f"/notes/{id}/view"
        )
        
        socketio.emit('new_notification', {
            'notification': notification
        }, broadcast=True)
```

**Ví dụ: Thông báo khi có comment mới**

```python
# Nếu có hệ thống comment
notification_storage.create_notification(
    title=f"💬 Comment mới trên note của bạn",
    message=f"{current_user.username}: {comment_text[:50]}...",
    type="info",
    user_id=note.user_id,
    link=f"/notes/{note_id}/view#comment-{comment_id}"
)
```

### Tích Hợp Email

```python
# Gửi email kèm theo thông báo
from flask_mail import Mail, Message

def send_notification_email(user_email, notification):
    msg = Message(
        subject=notification['title'],
        recipients=[user_email],
        body=notification['message']
    )
    mail.send(msg)
```

## Best Practices

1. **Không spam thông báo:**
   - Chỉ tạo thông báo cho sự kiện quan trọng
   - Gộp nhiều thông báo nhỏ thành 1 thông báo tổng hợp

2. **Tóm tắt rõ ràng:**
   - Loại bỏ HTML tags
   - Giới hạn độ dài hợp lý (50-150 ký tự)
   - Bao gồm thông tin quan trọng nhất

3. **Link chính xác:**
   - Luôn cung cấp link đến nội dung
   - Đảm bảo link hoạt động

4. **Error handling:**
   - Wrap trong try-except
   - Không để lỗi notification làm gián đoạn flow chính

5. **Performance:**
   - Cleanup thông báo cũ định kỳ
   - Giới hạn số lượng thông báo load mỗi lần

## Kết Luận

Hệ thống thông báo tự động giúp:
- ✅ Tăng tương tác giữa users
- ✅ Cập nhật thông tin real-time
- ✅ Không bỏ lỡ nội dung mới
- ✅ Tăng trải nghiệm người dùng

Mọi người đăng nhập sẽ luôn biết khi có note/document mới và có thể truy cập ngay lập tức!
