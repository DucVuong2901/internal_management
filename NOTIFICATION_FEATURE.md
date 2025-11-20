# Hệ Thống Thông Báo

## Tổng Quan

Hệ thống thông báo cho phép admin gửi thông báo đến người dùng và hiển thị chúng trong panel bên trái trang Chat.

## Tính Năng

### 1. **Notification Panel**
- Hiển thị ở bên trái trang Chat
- Responsive design (ẩn trên màn hình nhỏ < 992px)
- Hỗ trợ Dark Mode
- Tự động cập nhật số lượng thông báo chưa đọc

### 2. **Loại Thông Báo**
- **Info** (Thông tin): Màu xanh dương
- **Success** (Thành công): Màu xanh lá
- **Warning** (Cảnh báo): Màu vàng
- **Danger** (Quan trọng): Màu đỏ

### 3. **Chức Năng**
- ✅ Tạo thông báo (chỉ Admin)
- ✅ Xem danh sách thông báo
- ✅ Đánh dấu đã đọc khi click
- ✅ Đánh dấu tất cả đã đọc
- ✅ Thông báo broadcast (gửi cho tất cả)
- ✅ Thông báo riêng (gửi cho user cụ thể)
- ✅ Link đính kèm (chuyển hướng khi click)
- ✅ Real-time updates qua Socket.IO

## Cấu Trúc File

```
internal_management/
├── notification_storage.py      # Module quản lý thông báo
├── app.py                        # Routes API cho thông báo
├── templates/
│   └── chat.html                # UI notification panel
├── data/
│   └── notifications.json       # Lưu trữ thông báo
└── test_notifications.py        # Script tạo thông báo mẫu
```

## API Endpoints

### 1. Lấy danh sách thông báo
```
GET /notifications
Query params:
  - unread_only: true/false
  - limit: số lượng (default: 50)

Response:
{
  "success": true,
  "notifications": [...]
}
```

### 2. Đếm thông báo chưa đọc
```
GET /notifications/unread-count

Response:
{
  "success": true,
  "count": 5
}
```

### 3. Đánh dấu đã đọc
```
POST /notifications/<id>/read

Response:
{
  "success": true
}
```

### 4. Đánh dấu tất cả đã đọc
```
POST /notifications/mark-all-read

Response:
{
  "success": true,
  "count": 10
}
```

### 5. Tạo thông báo (Admin only)
```
POST /notifications/create
Content-Type: application/json

Body:
{
  "title": "Tiêu đề",
  "message": "Nội dung",
  "type": "info|success|warning|danger",
  "user_id": null,  // null = broadcast, số = user cụ thể
  "link": "/dashboard"  // optional
}

Response:
{
  "success": true,
  "notification": {...}
}
```

### 6. Xóa thông báo (Admin only)
```
POST /notifications/<id>/delete

Response:
{
  "success": true
}
```

## Socket.IO Events

### Client nhận:
- `new_notification`: Có thông báo mới
- `notification_deleted`: Thông báo bị xóa

## Sử Dụng

### 1. Tạo Thông Báo Mẫu
```bash
python test_notifications.py
```

### 2. Tạo Thông Báo Qua UI
1. Đăng nhập với tài khoản Admin
2. Vào trang Chat
3. Click nút "+" trong Notification Panel
4. Điền thông tin và submit

### 3. Tạo Thông Báo Qua Code
```python
from notification_storage import NotificationStorage

notification_storage = NotificationStorage(data_dir='data')

# Broadcast to all users
notification_storage.create_notification(
    title="Thông báo hệ thống",
    message="Nội dung thông báo",
    type="info",
    user_id=None,  # None = broadcast
    link="/dashboard"
)

# Gửi cho user cụ thể
notification_storage.create_notification(
    title="Thông báo riêng",
    message="Chỉ bạn nhìn thấy",
    type="warning",
    user_id=1,  # User ID
    link=None
)
```

## Tự Động Dọn Dẹp

Thông báo cũ hơn 30 ngày sẽ tự động bị xóa. Có thể tùy chỉnh:

```python
# Xóa thông báo cũ hơn 7 ngày
notification_storage.cleanup_old_notifications(days=7)
```

## Styling

### Light Mode
- Background: White
- Border: #e0e0e0
- Unread: Light blue (#f8f9ff)

### Dark Mode
- Background: #2d2d2d
- Border: #404040
- Unread: Dark blue (#2c3e50)

## Responsive Design

- Desktop (>992px): Panel hiển thị bên trái
- Tablet/Mobile (<992px): Panel ẩn (tiết kiệm không gian)

## Lưu Ý

1. **Quyền Admin**: Chỉ admin mới có thể tạo/xóa thông báo
2. **Storage**: Thông báo lưu trong `data/notifications.json`
3. **Real-time**: Cần Socket.IO để nhận thông báo real-time
4. **Performance**: Giới hạn 50 thông báo mỗi lần load

## Troubleshooting

### Không thấy thông báo?
1. Kiểm tra file `data/notifications.json` có tồn tại
2. Chạy `python test_notifications.py` để tạo thông báo mẫu
3. Refresh trang Chat

### Không nhận real-time updates?
1. Kiểm tra Socket.IO đang chạy
2. Xem console log có lỗi
3. Kiểm tra firewall/proxy

### Panel không hiển thị?
1. Kiểm tra màn hình >= 992px
2. Xem CSS có load đúng
3. Kiểm tra console có lỗi JavaScript

## Tích Hợp Với Các Module Khác

### Gửi thông báo khi có sự kiện:

```python
# Trong app.py hoặc module khác
from notification_storage import NotificationStorage

notification_storage = NotificationStorage(data_dir=DATA_DIR)

# Ví dụ: Khi user tạo document mới
@app.route('/docs/new', methods=['POST'])
def create_doc():
    # ... tạo document ...
    
    # Gửi thông báo cho admin
    notification_storage.create_notification(
        title="Document mới",
        message=f"{current_user.username} đã tạo document: {title}",
        type="info",
        user_id=admin_user_id,
        link=f"/docs/{doc_id}"
    )
    
    # Emit socket event
    socketio.emit('new_notification', {
        'notification': notification
    }, broadcast=True)
```

## Future Enhancements

- [ ] Notification preferences (user settings)
- [ ] Email notifications
- [ ] Push notifications
- [ ] Notification categories/filters
- [ ] Bulk actions
- [ ] Export notification history
- [ ] Notification templates
- [ ] Scheduled notifications
