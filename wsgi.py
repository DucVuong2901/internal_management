"""
WSGI entry point for production deployment
Sử dụng với Gunicorn hoặc uWSGI
"""
import os
import sys

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import application
from app import app, user_storage, file_storage

# Khởi tạo dữ liệu mặc định nếu cần
def init_default_data():
    """Khởi tạo dữ liệu mặc định khi chạy lần đầu"""
    # Tạo admin mặc định nếu chưa có
    if len(user_storage.get_all_users()) == 0:
        admin = user_storage.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com',
            role='admin'
        )
        if admin:
            print('=' * 50)
            print('TÀI KHOẢN ADMIN MẶC ĐỊNH:')
            print('Username: admin')
            print('Password: admin123')
            print('VUI LÒNG ĐỔI MẬT KHẨU SAU KHI ĐĂNG NHẬP!')
            print('=' * 50)
    
    # Tạo dữ liệu mẫu nếu chưa có
    notes = file_storage.get_all_notes()
    if len(notes) == 0:
        file_storage.create_note(
            title='Chào mừng!',
            content='Đây là ghi chú đầu tiên của bạn. Bạn có thể chỉnh sửa hoặc xóa nó.',
            category='general'
        )
    
    docs = file_storage.get_all_docs()
    if len(docs) == 0:
        file_storage.create_doc(
            title='Hướng dẫn sử dụng',
            content='''# Hướng dẫn sử dụng hệ thống

## Dashboard
Trang chủ hiển thị tổng quan về số lượng ghi chú và tài liệu.

## Ghi chú (Notes)
Tạo và quản lý các ghi chú cá nhân.

## Tài liệu (Documents)
Quản lý tài liệu nội bộ.

## Tìm kiếm
Sử dụng thanh tìm kiếm để tìm nhanh.
''',
            category='hướng dẫn'
        )

# Khởi tạo dữ liệu
init_default_data()

# Export application cho WSGI server
application = app

if __name__ == '__main__':
    # Chạy development server nếu gọi trực tiếp
    app.run()
