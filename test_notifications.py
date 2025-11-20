"""
Test script để tạo thông báo mẫu
Chạy script này để test hệ thống thông báo
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification_storage import NotificationStorage

def create_sample_notifications():
    """Tạo một số thông báo mẫu để test"""
    
    # Khởi tạo storage
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    notification_storage = NotificationStorage(data_dir=data_dir)
    
    print("=" * 60)
    print("TẠO THÔNG BÁO MẪU")
    print("=" * 60)
    
    # Thông báo 1: Info - Broadcast to all
    notif1 = notification_storage.create_notification(
        title="Chào mừng đến với hệ thống thông báo!",
        message="Bạn có thể nhận thông báo quan trọng từ admin ngay tại đây.",
        type="info",
        user_id=None,  # Broadcast to all users
        link="/dashboard"
    )
    print(f"✓ Đã tạo thông báo #{notif1['id']}: {notif1['title']}")
    
    # Thông báo 2: Success
    notif2 = notification_storage.create_notification(
        title="Cập nhật hệ thống thành công",
        message="Hệ thống đã được cập nhật lên phiên bản mới với nhiều tính năng cải tiến.",
        type="success",
        user_id=None,
        link=None
    )
    print(f"✓ Đã tạo thông báo #{notif2['id']}: {notif2['title']}")
    
    # Thông báo 3: Warning
    notif3 = notification_storage.create_notification(
        title="Bảo trì hệ thống",
        message="Hệ thống sẽ bảo trì vào 2h sáng ngày mai. Vui lòng lưu công việc trước đó.",
        type="warning",
        user_id=None,
        link=None
    )
    print(f"✓ Đã tạo thông báo #{notif3['id']}: {notif3['title']}")
    
    # Thông báo 4: Danger
    notif4 = notification_storage.create_notification(
        title="Cảnh báo bảo mật",
        message="Đã phát hiện hoạt động đăng nhập bất thường. Vui lòng đổi mật khẩu ngay.",
        type="danger",
        user_id=None,
        link="/change-password"
    )
    print(f"✓ Đã tạo thông báo #{notif4['id']}: {notif4['title']}")
    
    # Thông báo 5: Info cho user cụ thể (user_id=1)
    notif5 = notification_storage.create_notification(
        title="Thông báo riêng cho bạn",
        message="Đây là thông báo chỉ dành riêng cho tài khoản của bạn.",
        type="info",
        user_id=1,  # Chỉ user có ID=1 nhìn thấy
        link=None
    )
    print(f"✓ Đã tạo thông báo #{notif5['id']}: {notif5['title']} (user_id=1)")
    
    print("\n" + "=" * 60)
    print(f"HOÀN TẤT! Đã tạo 5 thông báo mẫu")
    print("=" * 60)
    
    # Hiển thị thống kê
    all_notifications = notification_storage.get_notifications(limit=100)
    print(f"\nTổng số thông báo trong hệ thống: {len(all_notifications)}")
    
    # Test đếm unread cho user 1
    unread_count = notification_storage.get_unread_count(user_id=1)
    print(f"Số thông báo chưa đọc cho user_id=1: {unread_count}")
    
    print("\n💡 Hướng dẫn:")
    print("1. Khởi động ứng dụng: python app.py")
    print("2. Đăng nhập vào hệ thống")
    print("3. Vào trang Chat để xem thông báo ở panel bên trái")
    print("4. Admin có thể tạo thông báo mới bằng nút '+' trong panel")
    print("\n🎯 Tính năng tự động:")
    print("- Khi tạo Note mới → Thông báo tự động gửi cho tất cả users")
    print("- Khi tạo Document mới → Thông báo tự động gửi cho tất cả users")
    print("- Thông báo bao gồm: Tiêu đề, Người tạo, Danh mục, Tóm tắt nội dung")
    print("- Click vào thông báo để xem chi tiết note/document")
    print("\n")

if __name__ == '__main__':
    create_sample_notifications()
