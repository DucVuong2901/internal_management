from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, session, send_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import json
import os
import re
import zipfile
import shutil
import tempfile
import logging
from logging.handlers import RotatingFileHandler

# Import custom storage modules
from csv_storage import CSVUserStorage, User
from file_storage import FileStorage, Note, Document

# Import configuration
from config import get_config

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
config_obj = get_config(config_name)

# Đảm bảo Flask tìm đúng thư mục templates và static
BASE_DIR = config_obj.BASE_DIR
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config.from_object(config_obj)

# Lấy các biến từ config
DOMAIN_NAME = app.config['DOMAIN_NAME']
DATA_DIR = app.config['DATA_DIR']

# Đảm bảo thư mục data tồn tại
os.makedirs(DATA_DIR, exist_ok=True)

# Khởi tạo storage - tất cả file dữ liệu trong thư mục data
user_storage = CSVUserStorage(csv_file=os.path.join(DATA_DIR, 'users.csv'))
file_storage = FileStorage(
    notes_dir=os.path.join(DATA_DIR, 'notes'),
    docs_dir=os.path.join(DATA_DIR, 'docs'),
    metadata_file=os.path.join(DATA_DIR, 'metadata.json'),
    uploads_dir=os.path.join(DATA_DIR, 'uploads')
)

# Edit logs storage
edit_logs_file = os.path.join(DATA_DIR, 'edit_logs.json')
# Categories storage
categories_file = os.path.join(DATA_DIR, 'categories.json')
# Chat storage
from chat_storage import ChatStorage
chat_storage = ChatStorage(data_dir=DATA_DIR)
# Notification storage
from notification_storage import NotificationStorage
notification_storage = NotificationStorage(data_dir=DATA_DIR)

# Scheduled tasks
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import atexit

# Khởi tạo scheduler với timezone
scheduler = BackgroundScheduler(timezone=utc)

# Task: Cleanup old messages mỗi 6 giờ
def cleanup_old_chat_messages():
    """Tự động xóa tin nhắn cũ hơn 48 giờ"""
    try:
        deleted = chat_storage._cleanup_old_messages()
        if deleted > 0:
            print(f"✓ Scheduled cleanup: Deleted {deleted} old messages")
            app.logger.info(f"Scheduled cleanup: Deleted {deleted} old messages")
    except Exception as e:
        print(f"✗ Scheduled cleanup error: {e}")
        app.logger.error(f"Scheduled cleanup error: {e}")

# Đăng ký task chạy mỗi 6 giờ
scheduler.add_job(
    func=cleanup_old_chat_messages,
    trigger='interval',
    hours=6,
    id='cleanup_chat_messages',
    name='Cleanup old chat messages (>48h)',
    replace_existing=True
)

# Start scheduler
scheduler.start()
print("✓ Scheduler started: Auto cleanup old messages every 6 hours")

# Shutdown scheduler khi app tắt
atexit.register(lambda: scheduler.shutdown())

# Setup logging
def setup_logging():
    """Cấu hình logging cho production"""
    if not app.debug:
        # Tạo thư mục logs nếu chưa có
        log_dir = os.path.join(DATA_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler với rotation (max 10MB, giữ 10 files backup)
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        
        # Format log
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Thêm handler vào app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Internal Management System startup')

setup_logging()

# Migration: Di chuyển users.csv từ thư mục gốc sang data/users.csv nếu cần
_old_users_file = os.path.join(BASE_DIR, 'users.csv')
_new_users_file = os.path.join(DATA_DIR, 'users.csv')
if os.path.exists(_old_users_file) and not os.path.exists(_new_users_file):
    try:
        import shutil
        shutil.move(_old_users_file, _new_users_file)
        print(f"✓ Đã di chuyển users.csv từ thư mục gốc sang {DATA_DIR}")
    except Exception as e:
        print(f"⚠ Cảnh báo: Không thể di chuyển users.csv: {e}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
login_manager.login_message_category = 'info'

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Xử lý lỗi 404 - Không tìm thấy trang"""
    app.logger.warning(f'404 error: {request.url}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Xử lý lỗi 500 - Lỗi server"""
    app.logger.error(f'500 error: {error}')
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Xử lý lỗi 403 - Không có quyền truy cập"""
    app.logger.warning(f'403 error: {request.url}')
    return render_template('errors/403.html'), 403

@app.errorhandler(413)
def request_entity_too_large(error):
    """Xử lý lỗi 413 - File quá lớn"""
    flash('File tải lên quá lớn! Vui lòng thử lại với file nhỏ hơn.', 'danger')
    return redirect(request.referrer or url_for('dashboard'))

@login_manager.user_loader
def load_user(user_id):
    return user_storage.get_user_by_id(user_id)

def load_edit_logs():
    """Load edit logs từ file JSON"""
    if not os.path.exists(edit_logs_file):
        return []
    try:
        with open(edit_logs_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def cleanup_old_logs(days=30):
    """Xóa các log cũ hơn số ngày chỉ định (mặc định 30 ngày)"""
    logs = load_edit_logs()
    if not logs:
        return 0
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    initial_count = len(logs)
    
    # Lọc các log còn trong thời hạn
    filtered_logs = []
    for log in logs:
        log_date = None
        created_at = log.get('created_at')
        
        # Xử lý created_at có thể là string hoặc datetime
        if isinstance(created_at, str):
            try:
                # Xử lý ISO format với hoặc không có timezone
                if 'Z' in created_at:
                    log_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    log_date = datetime.fromisoformat(created_at)
                
                # Chuyển về naive datetime (không có timezone) để so sánh
                if log_date.tzinfo is not None:
                    # Chuyển về UTC trước khi remove timezone
                    log_date = log_date.replace(tzinfo=None)
            except Exception as e:
                # Nếu không parse được, giữ lại log để an toàn
                filtered_logs.append(log)
                continue
        elif isinstance(created_at, datetime):
            log_date = created_at
            # Chuyển về naive datetime nếu có timezone
            if log_date.tzinfo is not None:
                log_date = log_date.replace(tzinfo=None)
        
        # Giữ lại log nếu còn trong thời hạn hoặc không xác định được ngày
        if log_date is None or log_date >= cutoff_date:
            filtered_logs.append(log)
    
    # Chỉ lưu lại nếu có thay đổi
    deleted_count = initial_count - len(filtered_logs)
    if deleted_count > 0:
        os.makedirs(os.path.dirname(edit_logs_file), exist_ok=True)
        with open(edit_logs_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_logs, f, ensure_ascii=False, indent=2)
    
    return deleted_count

def save_edit_log(log_data):
    """Lưu edit log vào file JSON"""
    logs = load_edit_logs()
    log_id = max([l.get('id', 0) for l in logs] + [0]) + 1
    log_data['id'] = log_id
    log_data['created_at'] = datetime.utcnow().isoformat()
    logs.append(log_data)
    
    os.makedirs(os.path.dirname(edit_logs_file), exist_ok=True)
    with open(edit_logs_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    # Tự động xóa log cũ hơn 30 ngày sau mỗi lần lưu log mới (để tránh check quá thường xuyên)
    # Chỉ cleanup mỗi 10 log để không làm chậm hệ thống
    if log_id % 10 == 0:
        cleanup_old_logs(30)

def load_categories():
    """Load categories từ file JSON - Hỗ trợ danh mục con"""
    if not os.path.exists(categories_file):
        # Tạo categories mặc định với cấu trúc hierarchical
        default_categories = {
            'general': {'name': 'general', 'parent': None, 'children': []},
            'công việc': {'name': 'công việc', 'parent': None, 'children': []},
            'cá nhân': {'name': 'cá nhân', 'parent': None, 'children': []},
            'học tập': {'name': 'học tập', 'parent': None, 'children': []},
            'quan trọng': {'name': 'quan trọng', 'parent': None, 'children': []},
            'hướng dẫn': {'name': 'hướng dẫn', 'parent': None, 'children': []}
        }
        save_categories(default_categories)
        return default_categories
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Backward compatibility: nếu là list cũ, convert sang dict mới
            if isinstance(data, list):
                new_data = {}
                for cat in data:
                    new_data[cat] = {'name': cat, 'parent': None, 'children': []}
                save_categories(new_data)
                return new_data
            return data
    except:
        return {'general': {'name': 'general', 'parent': None, 'children': []}}

def save_categories(categories):
    """Lưu categories vào file JSON"""
    os.makedirs(os.path.dirname(categories_file), exist_ok=True)
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def get_category_full_path(category_key, categories=None):
    """Lấy đường dẫn đầy đủ của category (parent > child)"""
    if categories is None:
        categories = load_categories()
    
    if category_key not in categories:
        return category_key
    
    cat = categories[category_key]
    display_name = cat.get('display_name', cat.get('name', category_key))
    
    if cat.get('parent'):
        parent_path = get_category_full_path(cat['parent'], categories)
        return f"{parent_path} > {display_name}"
    return display_name

def get_all_category_names(categories=None):
    """Lấy tất cả tên categories dưới dạng list (để backward compatibility)"""
    if categories is None:
        categories = load_categories()
    return list(categories.keys())

def get_root_categories(categories=None):
    """Lấy danh sách categories gốc (không có parent)"""
    if categories is None:
        categories = load_categories()
    return {k: v for k, v in categories.items() if not v.get('parent')}

def get_child_categories(parent_name, categories=None):
    """Lấy danh sách categories con của một parent"""
    if categories is None:
        categories = load_categories()
    
    if parent_name not in categories:
        return {}
    
    children = categories[parent_name].get('children', [])
    return {k: categories[k] for k in children if k in categories}

def process_pasted_images_in_content(note_id, content):
    """Xử lý các hình ảnh đã paste trong nội dung, chuyển thành attachment"""
    import re
    import uuid
    from werkzeug.utils import secure_filename
    
    # Tìm tất cả các img tag có src chứa /api/pasted-image/
    pattern = r'<img[^>]+src=["\']([^"\']*\/api\/pasted-image\/([^"\']+))["\'][^>]*>'
    matches = re.finditer(pattern, content)
    
    updated_content = content
    
    for match in matches:
        full_url = match.group(1)
        temp_filename = match.group(2)
        
        # Kiểm tra file có tồn tại không
        temp_path = os.path.join(file_storage.notes_uploads_dir, temp_filename)
        if not os.path.exists(temp_path):
            continue
        
        # Tạo tên file mới cho attachment
        file_ext = os.path.splitext(temp_filename)[1]
        unique_filename = f"{note_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        attachment_path = os.path.join(file_storage.notes_uploads_dir, unique_filename)
        
        # Tạo tên file gốc (bỏ prefix "pasted_" và timestamp)
        original_name = f"image{file_ext}"
        if temp_filename.startswith('pasted_'):
            # Có thể lấy tên gốc từ temp_filename nếu có
            parts = temp_filename.split('_')
            if len(parts) > 3:
                # Có thể có tên gốc sau user_id
                original_name = '_'.join(parts[3:]) if len(parts) > 3 else f"image{file_ext}"
        
        try:
            # Copy file từ temp location sang attachment location
            shutil.copy2(temp_path, attachment_path)
            
            # Thêm vào metadata của note
            metadata = file_storage._load_metadata()
            for note_meta in metadata.get('notes', []):
                if note_meta['id'] == int(note_id):
                    if 'attachments' not in note_meta:
                        note_meta['attachments'] = []
                    
                    note_meta['attachments'].append({
                        'filename': unique_filename,
                        'original_filename': secure_filename(original_name),
                        'uploaded_at': datetime.utcnow().isoformat()
                    })
                    note_meta['updated_at'] = datetime.utcnow().isoformat()
                    file_storage._save_metadata(metadata)
                    
                    # Tạo URL mới cho attachment
                    new_url = url_for('download_attachment', note_id=note_id, filename=unique_filename)
                    # Thay thế URL cũ bằng URL mới trong content
                    updated_content = updated_content.replace(full_url, new_url)
                    
                    # Xóa file tạm sau khi đã chuyển thành attachment
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    break
                    
        except Exception as e:
            print(f"Lỗi khi xử lý pasted image {temp_filename}: {str(e)}")
            continue
    
    return updated_content

# Decorators
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bạn cần quyền admin để truy cập trang này.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def can_edit_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role == 'viewer':
            flash('Bạn chỉ có quyền xem, không thể chỉnh sửa!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def can_create_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role == 'viewer':
            flash('Bạn chỉ có quyền xem, không thể tạo mới!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = user_storage.get_user_by_username(username)
        
        if user and user.check_password(password) and user.is_active:
            # Đăng nhập với remember=False (không dùng remember cookie)
            # Session sẽ tồn tại trong thời gian PERMANENT_SESSION_LIFETIME (1 giờ)
            login_user(user, remember=False)
            # Đặt session permanent để có timeout theo PERMANENT_SESSION_LIFETIME
            session.permanent = True
            next_page = request.args.get('next')
            flash(f'Chào mừng, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Đăng xuất và xóa session"""
    # Logout user - Flask-Login sẽ tự động xóa user khỏi session
    logout_user()
    
    # Flash message
    flash('Bạn đã đăng xuất thành công.', 'success')
    
    # Redirect về login
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Trang đổi mật khẩu cho user"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Mật khẩu mới và xác nhận không khớp!', 'danger')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'danger')
            return render_template('change_password.html')
        
        if new_password == current_password:
            flash('Mật khẩu mới phải khác mật khẩu hiện tại!', 'danger')
            return render_template('change_password.html')
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return render_template('change_password.html')
        
        # Update password
        success = user_storage.update_user(current_user.id, password=new_password)
        
        if success:
            # Log password change
            save_edit_log({
                'item_type': 'user',
                'item_id': current_user.id,
                'action': 'change_password',
                'user_id': current_user.id,
                'changes': json.dumps({
                    'action': f'User {current_user.username} đã đổi mật khẩu'
                })
            })
            flash('✓ Đã đổi mật khẩu thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Có lỗi xảy ra khi đổi mật khẩu!', 'danger')
    
    return render_template('change_password.html')

@app.before_request
def refresh_session():
    """
    Refresh session timeout mỗi request để giữ session sống trong khi user đang hoạt động.
    Session sẽ tự động hết hạn sau PERMANENT_SESSION_LIFETIME (1 giờ) kể từ request cuối cùng.
    """
    # Bỏ qua cho static files và login route
    if request.endpoint in ['login', 'static']:
        return None
    
    if request.path and request.path.startswith('/static/'):
        return None
    
    # Refresh session timeout nếu user đang đăng nhập
    if current_user.is_authenticated:
        session.modified = True  # Đánh dấu session đã thay đổi để Flask refresh timeout

@app.after_request
def set_no_cache_headers(response):
    """
Thiết lập headers để không cache trang (bảo mật)"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
@login_required
def dashboard():
    all_notes = file_storage.get_all_notes()
    all_docs = file_storage.get_all_docs()
    
    notes_count = len(all_notes)
    docs_count = len(all_docs)
    
    # Lấy tất cả categories và đếm số notes trong mỗi category
    categories_dict = load_categories()
    category_stats = {}
    
    for note in all_notes:
        cat = note.category
        if cat not in category_stats:
            category_stats[cat] = {
                'count': 0,
                'recent_note': None,
                'recent_date': None
            }
        category_stats[cat]['count'] += 1
        # Lấy note gần đây nhất trong category
        if not category_stats[cat]['recent_date'] or note.updated_at > category_stats[cat]['recent_date']:
            category_stats[cat]['recent_date'] = note.updated_at
            category_stats[cat]['recent_note'] = note
    
    # Chỉ lấy danh mục gốc (không có parent) và tính tổng count bao gồm cả children
    categories_with_stats = []
    for cat_name, cat_data in categories_dict.items():
        if not cat_data.get('parent'):  # Chỉ danh mục gốc
            # Tính tổng count của danh mục gốc + tất cả children
            total_count = category_stats.get(cat_name, {}).get('count', 0)
            recent_note = category_stats.get(cat_name, {}).get('recent_note')
            recent_date = category_stats.get(cat_name, {}).get('recent_date')
            
            # Thêm count từ children
            children_stats = []
            if cat_data.get('children'):
                for child_name in cat_data['children']:
                    child_count = category_stats.get(child_name, {}).get('count', 0)
                    total_count += child_count
                    
                    # Lưu stats của children để hiển thị
                    if child_count > 0:
                        children_stats.append({
                            'name': child_name,
                            'count': child_count,
                            'recent_note': category_stats.get(child_name, {}).get('recent_note'),
                            'recent_date': category_stats.get(child_name, {}).get('recent_date')
                        })
                    
                    # Cập nhật recent_note nếu child có note mới hơn
                    child_date = category_stats.get(child_name, {}).get('recent_date')
                    if child_date and (not recent_date or child_date > recent_date):
                        recent_date = child_date
                        recent_note = category_stats.get(child_name, {}).get('recent_note')
            
            categories_with_stats.append({
                'name': cat_name,
                'count': total_count,
                'recent_note': recent_note,
                'recent_date': recent_date,
                'children': children_stats,
                'has_children': len(children_stats) > 0
            })
    
    # Sắp xếp theo số lượng giảm dần
    categories_with_stats.sort(key=lambda x: x['count'], reverse=True)
    
    return render_template('dashboard.html', 
                         notes_count=notes_count,
                         docs_count=docs_count,
                         categories_with_stats=categories_with_stats,
                         categories_dict=categories_dict)

@app.route('/notes/<int:id>/view')
@login_required
def view_note(id):
    note = file_storage.get_note(id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    # Tăng số lần xem khi người dùng xem note
    file_storage.increment_note_view_count(id)
    return render_template('view_note.html', note=note)

@app.route('/notes/<int:id>/view/add-attachment', methods=['POST'])
@can_edit_required
def add_attachment_to_note(id):
    """Thêm file đính kèm từ trang xem note"""
    note = file_storage.get_note(id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    if 'attachments' in request.files:
        files = request.files.getlist('attachments')
        uploaded_count = 0
        for file in files:
            if file and file.filename:
                if file_storage.add_note_attachment(id, file):
                    uploaded_count += 1
        
        if uploaded_count > 0:
            flash(f'Đã thêm {uploaded_count} file đính kèm!', 'success')
        else:
            flash('Không có file nào được tải lên!', 'warning')
    
    return redirect(url_for('view_note', id=id))

@app.route('/category/<category_name>')
@login_required
def view_category(category_name):
    """Xem chi tiết một danh mục và các danh mục con của nó"""
    categories_dict = load_categories()
    
    if category_name not in categories_dict:
        flash('Danh mục không tồn tại!', 'danger')
        return redirect(url_for('dashboard'))
    
    cat_data = categories_dict[category_name]
    
    # Lấy thống kê cho danh mục này
    all_notes = file_storage.get_all_notes()
    
    # Count notes trong danh mục này
    parent_count = sum(1 for note in all_notes if note.category == category_name)
    
    # Lấy thống kê cho các danh mục con
    children_stats = []
    if cat_data.get('children'):
        for child_name in cat_data['children']:
            child_count = sum(1 for note in all_notes if note.category == child_name)
            recent_note = None
            recent_date = None
            
            for note in all_notes:
                if note.category == child_name:
                    if not recent_date or note.updated_at > recent_date:
                        recent_date = note.updated_at
                        recent_note = note
            
            children_stats.append({
                'name': child_name,
                'count': child_count,
                'recent_note': recent_note,
                'recent_date': recent_date
            })
    
    return render_template('view_category.html',
                         category_name=category_name,
                         category_data=cat_data,
                         parent_count=parent_count,
                         children_stats=children_stats)

@app.route('/notes')
@login_required
def notes():
    category = request.args.get('category', 'all')
    search_query = request.args.get('search', '')
    
    notes_list = file_storage.get_all_notes(category=category, search_query=search_query)
    categories = file_storage.get_note_categories()
    categories_dict = load_categories()
    
    # Thêm thông tin username cho mỗi note
    for note in notes_list:
        if note.user_id:
            creator = user_storage.get_user_by_id(note.user_id)
            note.creator_username = creator.username if creator else 'Không xác định'
        else:
            note.creator_username = 'Không xác định'
        
        if note.updated_by:
            updater = user_storage.get_user_by_id(note.updated_by)
            note.updater_username = updater.username if updater else 'Không xác định'
        else:
            note.updater_username = None
    
    return render_template('notes.html', 
                         notes=notes_list,
                         categories=categories,
                         categories_dict=categories_dict,
                         current_category=category,
                         search_query=search_query)

@app.route('/notes/new', methods=['GET', 'POST'])
@can_create_required
def new_note():
    categories_dict = load_categories()
    categories = get_all_category_names(categories_dict)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'general')
        
        # Kiểm tra title không rỗng (loại bỏ HTML tags để kiểm tra)
        title_text_only = re.sub(r'<[^>]+>', '', title).strip()
        if not title_text_only:
            flash('Tiêu đề không được để trống!', 'danger')
            return render_template('note_form.html', categories=categories, categories_dict=categories_dict)
        
        # Kiểm tra category có trong danh sách được phép
        if category not in categories:
            category = 'general'
            flash('Danh mục không hợp lệ, đã chuyển về danh mục mặc định.', 'warning')
        
        try:
            note = file_storage.create_note(
                title=title,
                content=content,
                category=category,
                user_id=current_user.id
            )
        except Exception as e:
            flash(f'Có lỗi xảy ra khi tạo ghi chú: {str(e)}', 'danger')
            return render_template('note_form.html', categories=categories, categories_dict=categories_dict)
        if note:
            # Xử lý file đính kèm
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if file_storage.add_note_attachment(note.id, file):
                            pass  # File đã được lưu
            
            # Không cần xử lý pasted images nữa vì chúng đã được thêm vào attachments
            
            # Log tạo mới với thông tin chi tiết
            save_edit_log({
                'item_type': 'note',
                'item_id': note.id,
                'action': 'create',
                'user_id': current_user.id,
                'changes': json.dumps({
                    'title': note.title,
                    'category': note.category,
                    'action': 'Tạo mới ghi chú'
                })
            })
            
            # Tạo thông báo cho tất cả users về note mới
            try:
                # Tạo tóm tắt nội dung (100 ký tự đầu, loại bỏ HTML)
                content_text = re.sub(r'<[^>]+>', '', content)
                content_summary = content_text[:100] + '...' if len(content_text) > 100 else content_text
                
                notification = notification_storage.create_notification(
                    title=f"📝 Note mới: {title}",
                    message=f"Người tạo: {current_user.username}\nDanh mục: {category}\n\n{content_summary}",
                    type="info",
                    user_id=None,  # Broadcast to all users
                    link=f"/notes/{note.id}/view"
                )
                
                # Emit socket event để notify realtime
                socketio.emit('new_notification', {
                    'notification': notification
                }, broadcast=True)
            except Exception as e:
                # Không làm gián đoạn flow nếu tạo notification lỗi
                app.logger.error(f"Error creating notification for new note: {e}")
            
            flash('✓ Đã lưu ghi chú thành công!', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Có lỗi xảy ra khi tạo ghi chú!', 'danger')
    return render_template('note_form.html', categories=categories, categories_dict=categories_dict)

@app.route('/notes/<int:id>/edit', methods=['GET', 'POST'])
@can_edit_required
def edit_note(id):
    note = file_storage.get_note(id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    categories_dict = load_categories()
    categories = get_all_category_names(categories_dict)
    
    # User và admin có thể chỉnh sửa tất cả ghi chú (không kiểm tra ownership)
    
    if request.method == 'POST':
        old_title = note.title
        old_category = note.category
        
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'general')
        
        # Validation
        if not title:
            flash('Tiêu đề không được để trống!', 'danger')
            return render_template('note_form.html', note=note, categories=categories, categories_dict=categories_dict)
        
        # Kiểm tra category có trong danh sách được phép
        if category not in categories:
            category = old_category
            flash('Danh mục không hợp lệ, giữ nguyên danh mục cũ.', 'warning')
        
        # Lưu thay đổi trước khi update
        changes = {
            'title': {'old': old_title, 'new': title},
            'content': {'old': note.content, 'new': content},  # Lưu toàn bộ nội dung, không chỉ preview
            'category': {'old': old_category, 'new': category}
        }
        
        try:
            success = file_storage.update_note(
                id,
                title=title,
                content=content,
                category=category,
                user_id=current_user.id
            )
        except Exception as e:
            flash(f'Có lỗi xảy ra khi cập nhật ghi chú: {str(e)}', 'danger')
            return render_template('note_form.html', note=note, categories=categories, categories_dict=categories_dict)
        
        if success:
            # Xử lý file đính kèm mới
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if file_storage.add_note_attachment(id, file):
                            pass  # File đã được lưu
            
            # Không cần xử lý pasted images nữa vì chúng đã được thêm vào attachments
            
            # Lấy note đã update để lấy updated_at (thời điểm sửa file)
            updated_note = file_storage.get_note(id)
            edit_timestamp = updated_note.updated_at if updated_note and updated_note.updated_at else datetime.utcnow()
            
            # Tạo log với thông tin chi tiết và thời điểm sửa file
            save_edit_log({
                'item_type': 'note',
                'item_id': id,
                'action': 'edit',
                'user_id': current_user.id,
                'changes': json.dumps(changes),
                'edit_timestamp': edit_timestamp.isoformat()  # Thời điểm sửa file
            })
            flash('✓ Đã lưu ghi chú thành công!', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Có lỗi xảy ra khi cập nhật!', 'danger')
    
    return render_template('note_form.html', note=note, categories=categories, categories_dict=categories_dict)

@app.route('/notes/<int:id>/delete', methods=['POST'])
@admin_required
def delete_note(id):
    # Chỉ admin mới được xóa
    note = file_storage.get_note(id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    # Tạo log trước khi xóa với thông tin chi tiết
    save_edit_log({
        'item_type': 'note',
        'item_id': id,
        'action': 'delete',
        'user_id': current_user.id,
        'changes': json.dumps({
            'title': note.title,
            'category': note.category,
            'action': 'Đã xóa ghi chú'
        })
    })
    
    file_storage.delete_note(id)
    flash('Ghi chú đã được xóa!', 'success')
    return redirect(url_for('notes'))

@app.route('/notes/<int:note_id>/picture/<filename>')
@login_required
def view_picture(note_id, filename):
    """Xem ảnh full screen"""
    note = file_storage.get_note(note_id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    # Kiểm tra file có thuộc note này không
    attachment_exists = any(
        (att.get('filename') if isinstance(att, dict) else getattr(att, 'filename', None)) == filename 
        for att in note.attachments
    )
    if not attachment_exists:
        flash('File không tồn tại!', 'danger')
        return redirect(url_for('view_note', id=note_id))
    
    # Kiểm tra có phải là hình ảnh không
    is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
    if not is_image:
        flash('File này không phải là hình ảnh!', 'danger')
        return redirect(url_for('view_note', id=note_id))
    
    # Tìm attachment info
    attachment_info = None
    for att in note.attachments:
        if (att.get('filename') if isinstance(att, dict) else getattr(att, 'filename', None)) == filename:
            attachment_info = att
            break
    
    original_filename = attachment_info.get('original_filename', filename) if attachment_info else filename
    image_url = url_for('download_attachment', note_id=note_id, filename=filename)
    
    return render_template('view_picture.html', 
                         note=note, 
                         filename=filename,
                         original_filename=original_filename,
                         image_url=image_url)

@app.route('/notes/<int:note_id>/attachment/<filename>')
@login_required
def download_attachment(note_id, filename):
    """Download hoặc xem file đính kèm"""
    note = file_storage.get_note(note_id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    # Tìm attachment info để lấy original_filename
    attachment_info = None
    for att in note.attachments:
        if (att.get('filename') if isinstance(att, dict) else getattr(att, 'filename', None)) == filename:
            attachment_info = att
            break
    
    if not attachment_info:
        flash('File không tồn tại!', 'danger')
        return redirect(url_for('view_note', id=note_id))
    
    # Lấy tên file gốc, nếu không có thì dùng filename hiện tại
    original_filename = attachment_info.get('original_filename', filename) if isinstance(attachment_info, dict) else getattr(attachment_info, 'original_filename', filename)
    
    # Nếu là hình ảnh, hiển thị trong browser, không force download
    is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
    
    return send_from_directory(
        file_storage.notes_uploads_dir,
        filename,
        as_attachment=not is_image,  # Force download nếu không phải hình ảnh
        download_name=original_filename  # Sử dụng tên file gốc khi download
    )

@app.route('/notes/<int:note_id>/attachment/<filename>/delete', methods=['POST'])
@can_edit_required
def delete_attachment(note_id, filename):
    """Xóa file đính kèm"""
    note = file_storage.get_note(note_id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    if file_storage.delete_note_attachment(note_id, filename):
        flash('File đã được xóa!', 'success')
    else:
        flash('Không thể xóa file!', 'danger')
    
    return redirect(url_for('edit_note', id=note_id))

@app.route('/docs')
@login_required
def docs():
    category = request.args.get('category', 'all')
    search_query = request.args.get('search', '')
    
    docs_list = file_storage.get_all_docs(category=category, search_query=search_query)
    categories = file_storage.get_doc_categories()
    categories_dict = load_categories()
    
    return render_template('docs.html',
                         docs=docs_list,
                         categories=categories,
                         categories_dict=categories_dict,
                         current_category=category,
                         search_query=search_query)

@app.route('/docs/new', methods=['GET', 'POST'])
@can_create_required
def new_doc():
    categories = load_categories()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'general')
        
        # Kiểm tra title không rỗng (loại bỏ HTML tags để kiểm tra)
        title_text_only = re.sub(r'<[^>]+>', '', title).strip()
        if not title_text_only:
            flash('Tiêu đề không được để trống!', 'danger')
            return render_template('doc_form.html', categories=categories)
        
        # Kiểm tra category có trong danh sách được phép
        if category not in categories:
            category = 'general'
            flash('Danh mục không hợp lệ, đã chuyển về danh mục mặc định.', 'warning')
        
        try:
            doc = file_storage.create_doc(
                title=title,
                content=content,
                category=category,
                user_id=current_user.id
            )
        except Exception as e:
            flash(f'Có lỗi xảy ra khi tạo tài liệu: {str(e)}', 'danger')
            return render_template('doc_form.html', categories=categories)
        if doc:
            # Xử lý file đính kèm
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if file_storage.add_doc_attachment(doc.id, file):
                            pass  # File đã được lưu
            
            # Log tạo mới với thông tin chi tiết
            save_edit_log({
                'item_type': 'doc',
                'item_id': doc.id,
                'action': 'create',
                'user_id': current_user.id,
                'changes': json.dumps({
                    'title': doc.title,
                    'category': doc.category,
                    'action': 'Tạo mới tài liệu'
                })
            })
            
            # Tạo thông báo cho tất cả users về document mới
            try:
                # Tạo tóm tắt nội dung (100 ký tự đầu, loại bỏ HTML)
                content_text = re.sub(r'<[^>]+>', '', content)
                content_summary = content_text[:100] + '...' if len(content_text) > 100 else content_text
                
                notification = notification_storage.create_notification(
                    title=f"📄 Tài liệu mới: {title}",
                    message=f"Người tạo: {current_user.username}\nDanh mục: {category}\n\n{content_summary}",
                    type="success",
                    user_id=None,  # Broadcast to all users
                    link=f"/docs/{doc.id}/view"
                )
                
                # Emit socket event để notify realtime
                socketio.emit('new_notification', {
                    'notification': notification
                }, broadcast=True)
            except Exception as e:
                # Không làm gián đoạn flow nếu tạo notification lỗi
                app.logger.error(f"Error creating notification for new document: {e}")
            
            flash('Tài liệu đã được tạo thành công!', 'success')
            return redirect(url_for('docs'))
        else:
            flash('Có lỗi xảy ra khi tạo tài liệu!', 'danger')
    return render_template('doc_form.html', categories=categories)

@app.route('/docs/<int:id>/view')
@login_required
def view_doc(id):
    doc = file_storage.get_doc(id)
    if not doc:
        flash('Tài liệu không tồn tại!', 'danger')
        return redirect(url_for('docs'))
    return render_template('view_doc.html', doc=doc)

@app.route('/docs/<int:id>/edit', methods=['GET', 'POST'])
@can_edit_required
def edit_doc(id):
    doc = file_storage.get_doc(id)
    if not doc:
        flash('Tài liệu không tồn tại!', 'danger')
        return redirect(url_for('docs'))
    
    categories = load_categories()
    
    # User và admin có thể chỉnh sửa tất cả tài liệu (không kiểm tra ownership)
    
    if request.method == 'POST':
        old_title = doc.title
        old_category = doc.category
        
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'general')
        
        # Validation
        if not title:
            flash('Tiêu đề không được để trống!', 'danger')
            return render_template('doc_form.html', doc=doc, categories=categories)
        
        # Kiểm tra category có trong danh sách được phép
        if category not in categories:
            category = old_category
            flash('Danh mục không hợp lệ, giữ nguyên danh mục cũ.', 'warning')
        
        # Lưu thay đổi trước khi update
        changes = {
            'title': {'old': old_title, 'new': title},
            'content': {'old': doc.content, 'new': content},  # Lưu toàn bộ nội dung, không chỉ preview
            'category': {'old': old_category, 'new': category}
        }
        
        try:
            success = file_storage.update_doc(
                id,
                title=title,
                content=content,
                category=category
            )
        except Exception as e:
            flash(f'Có lỗi xảy ra khi cập nhật tài liệu: {str(e)}', 'danger')
            return render_template('doc_form.html', doc=doc, categories=categories)
        
        if success:
            # Xử lý file đính kèm mới
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if file_storage.add_doc_attachment(id, file):
                            pass  # File đã được lưu
            
            # Lấy doc đã update để lấy updated_at (thời điểm sửa file)
            updated_doc = file_storage.get_doc(id)
            edit_timestamp = updated_doc.updated_at if updated_doc and updated_doc.updated_at else datetime.utcnow()
            
            # Tạo log với thông tin chi tiết và thời điểm sửa file
            save_edit_log({
                'item_type': 'doc',
                'item_id': id,
                'action': 'edit',
                'user_id': current_user.id,
                'changes': json.dumps(changes),
                'edit_timestamp': edit_timestamp.isoformat()  # Thời điểm sửa file
            })
            flash('Tài liệu đã được cập nhật!', 'success')
            return redirect(url_for('docs'))
        else:
            flash('Có lỗi xảy ra khi cập nhật!', 'danger')
    
    return render_template('doc_form.html', doc=doc, categories=categories)

@app.route('/docs/<int:id>/delete', methods=['POST'])
@admin_required
def delete_doc(id):
    # Chỉ admin mới được xóa
    doc = file_storage.get_doc(id)
    if not doc:
        flash('Tài liệu không tồn tại!', 'danger')
        return redirect(url_for('docs'))
    
    # Tạo log trước khi xóa với thông tin chi tiết
    save_edit_log({
        'item_type': 'doc',
        'item_id': id,
        'action': 'delete',
        'user_id': current_user.id,
        'changes': json.dumps({
            'title': doc.title,
            'category': doc.category,
            'action': 'Đã xóa tài liệu'
        })
    })
    
    file_storage.delete_doc(id)
    flash('Tài liệu đã được xóa!', 'success')
    return redirect(url_for('docs'))

@app.route('/docs/<int:doc_id>/attachment/<filename>')
@login_required
def download_doc_attachment(doc_id, filename):
    """Download hoặc xem file đính kèm của document"""
    doc = file_storage.get_doc(doc_id)
    if not doc:
        flash('Tài liệu không tồn tại!', 'danger')
        return redirect(url_for('docs'))
    
    # Tìm attachment info để lấy original_filename
    attachment_info = None
    for att in doc.attachments:
        if (att.get('filename') if isinstance(att, dict) else getattr(att, 'filename', None)) == filename:
            attachment_info = att
            break
    
    if not attachment_info:
        flash('File không tồn tại!', 'danger')
        return redirect(url_for('view_doc', id=doc_id))
    
    # Lấy tên file gốc, nếu không có thì dùng filename hiện tại
    original_filename = attachment_info.get('original_filename', filename) if isinstance(attachment_info, dict) else getattr(attachment_info, 'original_filename', filename)
    
    # Nếu là hình ảnh, hiển thị trong browser, không force download
    is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
    
    return send_from_directory(
        file_storage.docs_uploads_dir,
        filename,
        as_attachment=not is_image,  # Force download nếu không phải hình ảnh
        download_name=original_filename  # Sử dụng tên file gốc khi download
    )

@app.route('/docs/<int:doc_id>/attachment/<filename>/delete', methods=['POST'])
@can_edit_required
def delete_doc_attachment(doc_id, filename):
    """Xóa file đính kèm của document"""
    doc = file_storage.get_doc(doc_id)
    if not doc:
        flash('Tài liệu không tồn tại!', 'danger')
        return redirect(url_for('docs'))
    
    if file_storage.delete_doc_attachment(doc_id, filename):
        flash('File đã được xóa!', 'success')
    else:
        flash('Không thể xóa file!', 'danger')
    
    return redirect(url_for('edit_doc', id=doc_id))

@app.route('/docs/<int:id>/view/add-attachment', methods=['POST'])
@can_edit_required
def add_attachment_to_doc(id):
    """Thêm file đính kèm từ trang xem doc"""
    doc = file_storage.get_doc(id)
    if not doc:
        flash('Tài liệu không tồn tại!', 'danger')
        return redirect(url_for('docs'))
    
    if 'attachments' in request.files:
        files = request.files.getlist('attachments')
        uploaded_count = 0
        for file in files:
            if file and file.filename:
                if file_storage.add_doc_attachment(id, file):
                    uploaded_count += 1
        
        if uploaded_count > 0:
            flash(f'Đã thêm {uploaded_count} file đính kèm!', 'success')
        else:
            flash('Không có file nào được tải lên!', 'warning')
    
    return redirect(url_for('view_doc', id=id))

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    results = {'notes': [], 'docs': []}
    
    if query:
        results['notes'] = file_storage.get_all_notes(search_query=query)
        results['docs'] = file_storage.get_all_docs(search_query=query)
    
    return render_template('search.html', query=query, results=results)

@app.route('/api/search')
@login_required
def api_search():
    query = request.args.get('q', '')
    results = {'notes': [], 'docs': []}
    
    if query:
        notes = file_storage.get_all_notes(search_query=query)[:5]
        docs = file_storage.get_all_docs(search_query=query)[:5]
        
        results['notes'] = [{'id': n.id, 'title': n.title, 'type': 'note'} for n in notes]
        results['docs'] = [{'id': d.id, 'title': d.title, 'type': 'doc'} for d in docs]
    
    return jsonify(results)

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint để logout - không redirect, trả về JSON - không cần @login_required vì có thể session đã hết"""
    try:
        # Logout user nếu đang đăng nhập
        if current_user.is_authenticated:
            logout_user()
        # Xóa session
        session.clear()
        response = jsonify({'status': 'success', 'message': 'Đã đăng xuất'})
        # Xóa cookie session
        response.set_cookie('session', '', expires=0, max_age=0)
        return response
    except Exception as e:
        # Ngay cả khi có lỗi, vẫn cố gắng xóa session
        try:
            session.clear()
            response = jsonify({'status': 'success', 'message': 'Đã đăng xuất'})
            response.set_cookie('session', '', expires=0, max_age=0)
            return response
        except:
            return jsonify({'status': 'success', 'message': 'Đã đăng xuất'}), 200

@app.route('/api/check_session')
@login_required
def api_check_session():
    """API endpoint để kiểm tra session còn hiệu lực không"""
    # Nếu đến được đây nghĩa là session còn hợp lệ (vì đã pass @login_required)
    return jsonify({'valid': True, 'username': current_user.username}), 200

@app.route('/api/upload-pasted-image', methods=['POST'])
@login_required
def upload_pasted_image():
    """API endpoint để upload hình ảnh từ clipboard paste"""
    try:
        # Kiểm tra có file trong request không
        if 'image' not in request.files:
            return jsonify({'error': 'Không có hình ảnh'}), 400
        
        file = request.files['image']
        
        # Kiểm tra file có tồn tại và có filename không
        if not file or not file.filename:
            # Nếu không có filename, có thể là dữ liệu base64
            # Kiểm tra xem có dữ liệu trong request form không
            if 'data' in request.form:
                # Xử lý base64 data
                import base64
                data = request.form.get('data')
                if not data or not data.startswith('data:image'):
                    return jsonify({'error': 'Dữ liệu hình ảnh không hợp lệ'}), 400
                
                # Parse base64 data
                header, encoded = data.split(',', 1)
                image_data = base64.b64decode(encoded)
                
                # Xác định extension từ header
                if 'png' in header:
                    ext = 'png'
                elif 'jpeg' in header or 'jpg' in header:
                    ext = 'jpg'
                elif 'gif' in header:
                    ext = 'gif'
                elif 'webp' in header:
                    ext = 'webp'
                else:
                    ext = 'png'
                
                # Tạo tên file tạm
                filename = f"pasted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}.{ext}"
                temp_path = os.path.join(file_storage.notes_uploads_dir, filename)
                
                # Lưu file
                with open(temp_path, 'wb') as f:
                    f.write(image_data)
                
                # Tạo URL tạm để trả về
                image_url = url_for('download_pasted_image', filename=filename)
                return jsonify({
                    'success': True,
                    'url': image_url,
                    'filename': filename
                })
            else:
                return jsonify({'error': 'Không có dữ liệu hình ảnh'}), 400
        
        # Kiểm tra file có phải là hình ảnh không
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            return jsonify({'error': 'File phải là hình ảnh'}), 400
        
        # Lưu file vào thư mục uploads tạm
        filename = secure_filename(file.filename)
        # Thêm timestamp và user_id để tránh trùng tên
        name, ext = os.path.splitext(filename)
        filename = f"pasted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}_{name}{ext}"
        filepath = os.path.join(file_storage.notes_uploads_dir, filename)
        file.save(filepath)
        
        # Tạo URL để trả về
        image_url = url_for('download_pasted_image', filename=filename)
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': f'Lỗi khi upload: {str(e)}'}), 500

@app.route('/api/pasted-image/<filename>')
@login_required
def download_pasted_image(filename):
    """Download hình ảnh đã paste (tạm thời)"""
    # Kiểm tra file có tồn tại không
    filepath = os.path.join(file_storage.notes_uploads_dir, filename)
    if not os.path.exists(filepath):
        flash('File không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    # Kiểm tra file có phải là hình ảnh không
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
        flash('File không phải là hình ảnh!', 'danger')
        return redirect(url_for('notes'))
    
    return send_from_directory(
        file_storage.notes_uploads_dir,
        filename,
        as_attachment=False
    )

# User Management Routes (Admin only)
@app.route('/admin/users')
@admin_required
def manage_users():
    users = user_storage.get_all_users()
    # Sort by created_at descending
    users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    # Convert to User objects for template compatibility
    user_objects = [user_storage._dict_to_user(u) for u in users]
    return render_template('manage_users.html', users=user_objects)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@admin_required
def new_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email', '')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        user = user_storage.create_user(
            username=username,
            password=password,
            email=email if email else None,
            role=role
        )
        
        if user:
            # Tạo log
            save_edit_log({
                'item_type': 'user',
                'item_id': user.id,
                'action': 'create',
                'user_id': current_user.id,
                'changes': json.dumps({'username': username, 'role': role, 'action': f'Tạo người dùng mới: {username} với quyền {role}'})
            })
            flash(f'Người dùng {username} đã được tạo thành công!', 'success')
            return redirect(url_for('manage_users'))
        else:
            flash('Tên đăng nhập hoặc email đã tồn tại!', 'danger')
    
    return render_template('user_form.html')

@app.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = user_storage.get_user_by_id(id)
    if not user:
        flash('Người dùng không tồn tại!', 'danger')
        return redirect(url_for('manage_users'))
    
    if request.method == 'POST':
        old_username = user.username
        old_role = user.role
        
        username = request.form.get('username')
        email = request.form.get('email', '')
        role = request.form.get('role', 'user')
        password = request.form.get('password')
        is_active = request.form.get('is_active') == 'on'
        
        changes = {
            'username': {'old': old_username, 'new': username},
            'role': {'old': old_role, 'new': role},
            'is_active': {'old': user.is_active, 'new': is_active}
        }
        if password:
            changes['password'] = 'Đã đổi mật khẩu'
        
        success = user_storage.update_user(
            id,
            username=username,
            email=email if email else None,
            role=role,
            password=password if password else None,
            is_active=is_active
        )
        
        if success:
            save_edit_log({
                'item_type': 'user',
                'item_id': id,
                'action': 'edit',
                'user_id': current_user.id,
                'changes': json.dumps(changes)
            })
            flash(f'Người dùng {username} đã được cập nhật!', 'success')
            return redirect(url_for('manage_users'))
        else:
            flash('Tên đăng nhập hoặc email đã tồn tại!', 'danger')
    
    return render_template('user_form.html', user=user)

@app.route('/admin/users/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    user = user_storage.get_user_by_id(id)
    if not user:
        flash('Người dùng không tồn tại!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Không cho phép xóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể xóa chính mình!', 'danger')
        return redirect(url_for('manage_users'))
    
    username = user.username
    user_storage.delete_user(id)
    save_edit_log({
        'item_type': 'user',
        'item_id': id,
        'action': 'delete',
        'user_id': current_user.id,
        'changes': json.dumps({'username': username, 'action': f'Đã xóa người dùng: {username}'})
    })
    flash(f'Người dùng {username} đã được xóa!', 'success')
    return redirect(url_for('manage_users'))

# Categories Management (Admin only)
@app.route('/admin/categories')
@admin_required
def manage_categories():
    categories = load_categories()
    return render_template('manage_categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
@admin_required
def add_category():
    category = request.form.get('category', '').strip().lower()
    parent = request.form.get('parent', '').strip().lower() if request.form.get('parent', '').strip() else None
    
    if not category:
        flash('Tên danh mục không được để trống!', 'danger')
        return redirect(url_for('manage_categories'))
    
    categories = load_categories()
    
    # Tạo unique key: nếu có parent thì "parent/child", nếu không thì chỉ "category"
    if parent:
        category_key = f"{parent}/{category}"
    else:
        category_key = category
    
    # Kiểm tra key đã tồn tại chưa
    if category_key in categories:
        if parent:
            flash(f'❌ Danh mục con "{category}" đã tồn tại trong "{parent}"!', 'danger')
        else:
            flash(f'❌ Danh mục gốc "{category}" đã tồn tại!', 'danger')
        return redirect(url_for('manage_categories'))
    
    # Kiểm tra parent có tồn tại không
    if parent and parent not in categories:
        flash(f'❌ Danh mục cha "{parent}" không tồn tại!', 'danger')
        return redirect(url_for('manage_categories'))
    
    # Kiểm tra không thể tạo danh mục con của chính nó
    if parent == category:
        flash(f'❌ Không thể tạo danh mục con của chính nó!', 'danger')
        return redirect(url_for('manage_categories'))
    
    # Thêm category mới với key unique
    categories[category_key] = {
        'name': category,
        'parent': parent,
        'children': [],
        'display_name': category  # Tên hiển thị
    }
    
    # Cập nhật children của parent
    if parent:
        if 'children' not in categories[parent]:
            categories[parent]['children'] = []
        categories[parent]['children'].append(category_key)
    
    save_categories(categories)
    
    if parent:
        flash(f'✓ Danh mục con "{category}" đã được thêm vào "{parent}"!', 'success')
    else:
        flash(f'✓ Danh mục "{category}" đã được thêm!', 'success')
    
    return redirect(url_for('manage_categories'))

@app.route('/admin/categories/fix-orphans', methods=['POST'])
@admin_required
def fix_orphan_categories():
    """Fix các danh mục con bị orphan (parent không đúng)"""
    categories = load_categories()
    fixed_count = 0
    
    # Tìm các danh mục có parent nhưng không nằm trong children của parent
    for cat_name, cat_data in list(categories.items()):
        parent = cat_data.get('parent')
        if parent and parent in categories:
            # Kiểm tra xem cat_name có trong children của parent không
            if cat_name not in categories[parent].get('children', []):
                # Thêm vào children
                if 'children' not in categories[parent]:
                    categories[parent]['children'] = []
                categories[parent]['children'].append(cat_name)
                fixed_count += 1
    
    if fixed_count > 0:
        save_categories(categories)
        flash(f'✓ Đã sửa {fixed_count} danh mục con!', 'success')
    else:
        flash('Không có danh mục nào cần sửa.', 'info')
    
    return redirect(url_for('manage_categories'))

@app.route('/admin/categories/delete', methods=['POST'])
@admin_required
def delete_category():
    category = request.form.get('category', '').strip()
    if category and category != 'general':
        categories = load_categories()
        if category in categories:
            cat_data = categories[category]
            
            # Kiểm tra xem có danh mục con không
            if cat_data.get('children'):
                flash(f'Không thể xóa danh mục "{category}" vì còn có danh mục con!', 'danger')
                return redirect(url_for('manage_categories'))
            
            # Xóa khỏi children của parent (nếu có)
            parent = cat_data.get('parent')
            if parent and parent in categories:
                if category in categories[parent].get('children', []):
                    categories[parent]['children'].remove(category)
            
            # Xóa category
            del categories[category]
            save_categories(categories)
            flash(f'Danh mục "{category}" đã được xóa!', 'success')
        else:
            flash(f'Danh mục "{category}" không tồn tại!', 'warning')
    else:
        flash('Không thể xóa danh mục "general"!', 'danger')
    return redirect(url_for('manage_categories'))

@app.route('/admin/edit-logs')
@admin_required
def edit_logs():
    # Tự động xóa log cũ hơn 30 ngày khi vào trang edit logs
    deleted_count = cleanup_old_logs(30)
    if deleted_count > 0:
        flash(f'Đã tự động xóa {deleted_count} log cũ hơn 30 ngày.', 'info')
    
    logs = load_edit_logs()
    
    # Convert created_at và edit_timestamp từ string sang datetime và xử lý logs
    for log in logs:
        # Ưu tiên dùng edit_timestamp (thời điểm sửa file) nếu có, nếu không thì dùng created_at
        if log.get('edit_timestamp'):
            if isinstance(log.get('edit_timestamp'), str):
                try:
                    log['display_time'] = datetime.fromisoformat(log['edit_timestamp'])
                except:
                    log['display_time'] = None
            else:
                log['display_time'] = log.get('edit_timestamp')
        else:
            # Fallback về created_at nếu không có edit_timestamp
            if isinstance(log.get('created_at'), str):
                try:
                    log['display_time'] = datetime.fromisoformat(log['created_at'])
                except:
                    log['display_time'] = None
            else:
                log['display_time'] = log.get('created_at')
        
        # Convert created_at từ ISO string sang datetime object (giữ lại để sort)
        if isinstance(log.get('created_at'), str):
            try:
                log['created_at'] = datetime.fromisoformat(log['created_at'])
            except:
                log['created_at'] = None
        
        # Convert user_id thành username để hiển thị
        user = user_storage.get_user_by_id(log.get('user_id'))
        log['username'] = user.username if user else 'Unknown'
        
        # Parse changes JSON nếu là string
        if isinstance(log.get('changes'), str):
            try:
                log['changes'] = json.loads(log['changes'])
            except:
                pass
    
    # Sort by created_at descending và limit 100
    logs.sort(key=lambda x: x.get('created_at', datetime.min) if isinstance(x.get('created_at'), datetime) else datetime.min, reverse=True)
    logs = logs[:100]
    
    return render_template('edit_logs.html', logs=logs)

# Export/Import Data Routes (Admin only)
@app.route('/admin/export-import')
@admin_required
def export_import():
    """Trang quản lý export/import dữ liệu"""
    return render_template('export_import.html')

@app.route('/admin/export', methods=['POST'])
@admin_required
def export_data():
    """Export toàn bộ dữ liệu ra file ZIP"""
    try:
        # Tạo file ZIP tạm
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'backup_{timestamp}.zip'
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Export users.csv
            if os.path.exists(user_storage.csv_file):
                zipf.write(user_storage.csv_file, 'users.csv')
            
            # 2. Export metadata.json (chứa notes và docs metadata)
            if os.path.exists(file_storage.metadata_file):
                zipf.write(file_storage.metadata_file, 'metadata.json')
            
            # 3. Export categories.json
            if os.path.exists(categories_file):
                zipf.write(categories_file, 'categories.json')
            
            # 4. Export edit_logs.json
            if os.path.exists(edit_logs_file):
                zipf.write(edit_logs_file, 'edit_logs.json')
            
            # 5. Export thư mục notes (tất cả file .txt)
            if os.path.exists(file_storage.notes_dir):
                for root, dirs, files in os.walk(file_storage.notes_dir):
                    for file in files:
                        if file.endswith('.txt'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('notes', file)
                            zipf.write(file_path, arcname)
            
            # 6. Export thư mục docs (tất cả file .txt)
            if os.path.exists(file_storage.docs_dir):
                for root, dirs, files in os.walk(file_storage.docs_dir):
                    for file in files:
                        if file.endswith('.txt'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('docs', file)
                            zipf.write(file_path, arcname)
            
            # 7. Export attachments từ notes
            if os.path.exists(file_storage.notes_uploads_dir):
                for root, dirs, files in os.walk(file_storage.notes_uploads_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join('uploads', 'notes', file)
                        zipf.write(file_path, arcname)
            
            # 8. Export attachments từ docs
            if os.path.exists(file_storage.docs_uploads_dir):
                for root, dirs, files in os.walk(file_storage.docs_uploads_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join('uploads', 'docs', file)
                        zipf.write(file_path, arcname)
        
        # Log export action
        save_edit_log({
            'item_type': 'system',
            'item_id': 0,
            'action': 'export',
            'user_id': current_user.id,
            'changes': json.dumps({
                'filename': zip_filename,
                'action': 'Xuất dữ liệu hệ thống'
            })
        })
        
        # Gửi file về client
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
    
    except Exception as e:
        flash(f'Lỗi khi export dữ liệu: {str(e)}', 'danger')
        return redirect(url_for('export_import'))

@app.route('/admin/import', methods=['POST'])
@admin_required
def import_data():
    """Import dữ liệu từ file ZIP"""
    if 'import_file' not in request.files:
        flash('Vui lòng chọn file để import!', 'danger')
        return redirect(url_for('export_import'))
    
    file = request.files['import_file']
    
    # Kiểm tra file có tồn tại và là FileStorage object
    if not file or not hasattr(file, 'filename'):
        flash('File upload không hợp lệ!', 'danger')
        return redirect(url_for('export_import'))
    
    # Kiểm tra filename có tồn tại và không rỗng
    original_filename = getattr(file, 'filename', None)
    if not original_filename or original_filename == '' or original_filename == 'None':
        flash('Vui lòng chọn file để import!', 'danger')
        return redirect(url_for('export_import'))
    
    if not original_filename.endswith('.zip'):
        flash('File phải có định dạng .zip!', 'danger')
        return redirect(url_for('export_import'))
    
    # Kiểm tra xác nhận import
    import_mode = request.form.get('import_mode', 'merge')  # merge hoặc replace
    
    try:
        # Lưu file tạm
        temp_dir = tempfile.mkdtemp()
        temp_zip_path = os.path.join(temp_dir, secure_filename(original_filename))
        file.save(temp_zip_path)
        
        # Giải nén ZIP
        extract_dir = os.path.join(temp_dir, 'extract')
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        import_count = {
            'users': 0,
            'notes': 0,
            'docs': 0,
            'attachments': 0
        }
        
        # 1. Import users.csv (chỉ trong mode replace vì merge users phức tạp và nguy hiểm)
        users_file = os.path.join(extract_dir, 'users.csv')
        if os.path.exists(users_file):
            if import_mode == 'replace':
                # Backup file cũ
                if os.path.exists(user_storage.csv_file):
                    backup_file = user_storage.csv_file + '.backup'
                    shutil.copy2(user_storage.csv_file, backup_file)
                # Copy file mới
                os.makedirs(os.path.dirname(user_storage.csv_file), exist_ok=True)
                shutil.copy2(users_file, user_storage.csv_file)
                # Verify file was copied successfully
                if os.path.exists(user_storage.csv_file):
                    # Đếm số users đã import
                    import_count['users'] = len(user_storage.get_all_users())
                    print(f"DEBUG: Imported {import_count['users']} users from {users_file}")
                else:
                    print(f"DEBUG: Failed to copy users file to {user_storage.csv_file}")
            # Note: Merge mode không import users để tránh xung đột password hash và quyền admin
        
        # 2. Import metadata.json
        metadata_file = os.path.join(extract_dir, 'metadata.json')
        if os.path.exists(metadata_file):
            if import_mode == 'replace':
                # Backup file cũ
                if os.path.exists(file_storage.metadata_file):
                    backup_file = file_storage.metadata_file + '.backup'
                    shutil.copy2(file_storage.metadata_file, backup_file)
                # Copy file mới
                os.makedirs(os.path.dirname(file_storage.metadata_file), exist_ok=True)
                shutil.copy2(metadata_file, file_storage.metadata_file)
            else:
                # Merge mode: đọc cả hai và merge
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    imported_metadata = json.load(f)
                current_metadata = file_storage._load_metadata()
                
                # Merge notes
                imported_note_ids = {n['id'] for n in imported_metadata.get('notes', [])}
                current_metadata['notes'] = [n for n in current_metadata.get('notes', []) 
                                           if n['id'] not in imported_note_ids]
                current_metadata['notes'].extend(imported_metadata.get('notes', []))
                import_count['notes'] = len(imported_metadata.get('notes', []))
                
                # Merge docs
                imported_doc_ids = {d['id'] for d in imported_metadata.get('docs', [])}
                current_metadata['docs'] = [d for d in current_metadata.get('docs', []) 
                                          if d['id'] not in imported_doc_ids]
                current_metadata['docs'].extend(imported_metadata.get('docs', []))
                import_count['docs'] = len(imported_metadata.get('docs', []))
                
                file_storage._save_metadata(current_metadata)
        
        # 3. Import categories.json
        categories_file_import = os.path.join(extract_dir, 'categories.json')
        if os.path.exists(categories_file_import):
            with open(categories_file_import, 'r', encoding='utf-8') as f:
                imported_categories = json.load(f)
            if import_mode == 'replace':
                save_categories(imported_categories)
            else:
                # Merge categories
                current_categories = load_categories()
                for cat in imported_categories:
                    if cat not in current_categories:
                        current_categories.append(cat)
                save_categories(current_categories)
        
        # 4. Import edit_logs.json
        edit_logs_file_import = os.path.join(extract_dir, 'edit_logs.json')
        if os.path.exists(edit_logs_file_import):
            with open(edit_logs_file_import, 'r', encoding='utf-8') as f:
                imported_logs = json.load(f)
            if import_mode == 'replace':
                os.makedirs(os.path.dirname(edit_logs_file), exist_ok=True)
                shutil.copy2(edit_logs_file_import, edit_logs_file)
            else:
                # Merge logs
                current_logs = load_edit_logs()
                imported_log_ids = {l.get('id') for l in imported_logs}
                current_logs = [l for l in current_logs if l.get('id') not in imported_log_ids]
                current_logs.extend(imported_logs)
                os.makedirs(os.path.dirname(edit_logs_file), exist_ok=True)
                with open(edit_logs_file, 'w', encoding='utf-8') as f:
                    json.dump(current_logs, f, ensure_ascii=False, indent=2)
        
        # 5. Import notes files
        notes_dir_import = os.path.join(extract_dir, 'notes')
        if os.path.exists(notes_dir_import):
            if import_mode == 'replace':
                # Xóa thư mục cũ và copy mới
                if os.path.exists(file_storage.notes_dir):
                    shutil.rmtree(file_storage.notes_dir)
                shutil.copytree(notes_dir_import, file_storage.notes_dir)
            else:
                # Merge mode: Copy các file mới, thay thế file cũ nếu cùng ID
                os.makedirs(file_storage.notes_dir, exist_ok=True)
                for root, dirs, files in os.walk(notes_dir_import):
                    for filename in files:
                        if filename.endswith('.txt'):
                            src = os.path.join(root, filename)
                            dst = os.path.join(file_storage.notes_dir, filename)
                            # Trong merge mode, luôn copy để thay thế file cũ nếu trùng ID
                            shutil.copy2(src, dst)
        
        # 6. Import docs files
        docs_dir_import = os.path.join(extract_dir, 'docs')
        if os.path.exists(docs_dir_import):
            if import_mode == 'replace':
                # Xóa thư mục cũ và copy mới
                if os.path.exists(file_storage.docs_dir):
                    shutil.rmtree(file_storage.docs_dir)
                shutil.copytree(docs_dir_import, file_storage.docs_dir)
            else:
                # Merge mode: Copy các file mới, thay thế file cũ nếu cùng ID
                os.makedirs(file_storage.docs_dir, exist_ok=True)
                for root, dirs, files in os.walk(docs_dir_import):
                    for filename in files:
                        if filename.endswith('.txt'):
                            src = os.path.join(root, filename)
                            dst = os.path.join(file_storage.docs_dir, filename)
                            # Trong merge mode, luôn copy để thay thế file cũ nếu trùng ID
                            shutil.copy2(src, dst)
        
        # 7. Import attachments từ notes
        notes_uploads_dir_import = os.path.join(extract_dir, 'uploads', 'notes')
        if os.path.exists(notes_uploads_dir_import):
            os.makedirs(file_storage.notes_uploads_dir, exist_ok=True)
            for root, dirs, files in os.walk(notes_uploads_dir_import):
                for filename in files:
                    src = os.path.join(root, filename)
                    dst = os.path.join(file_storage.notes_uploads_dir, filename)
                    # Luôn copy để đảm bảo file mới nhất được sử dụng
                    shutil.copy2(src, dst)
                    import_count['attachments'] += 1
        
        # 8. Import attachments từ docs
        docs_uploads_dir_import = os.path.join(extract_dir, 'uploads', 'docs')
        if os.path.exists(docs_uploads_dir_import):
            os.makedirs(file_storage.docs_uploads_dir, exist_ok=True)
            for root, dirs, files in os.walk(docs_uploads_dir_import):
                for filename in files:
                    src = os.path.join(root, filename)
                    dst = os.path.join(file_storage.docs_uploads_dir, filename)
                    # Luôn copy để đảm bảo file mới nhất được sử dụng
                    shutil.copy2(src, dst)
                    import_count['attachments'] += 1
        
        # Dọn dẹp file tạm
        shutil.rmtree(temp_dir)
        
        # Log import action
        save_edit_log({
            'item_type': 'system',
            'item_id': 0,
            'action': 'import',
            'user_id': current_user.id,
            'changes': json.dumps({
                'filename': original_filename,
                'mode': import_mode,
                'imported': import_count,
                'action': 'Nhập dữ liệu hệ thống'
            })
        })
        
        # Tạo message chi tiết
        msg_parts = []
        if import_count["users"] > 0:
            msg_parts.append(f'{import_count["users"]} người dùng')
        if import_count["notes"] > 0:
            msg_parts.append(f'{import_count["notes"]} ghi chú')
        if import_count["docs"] > 0:
            msg_parts.append(f'{import_count["docs"]} tài liệu')
        if import_count["attachments"] > 0:
            msg_parts.append(f'{import_count["attachments"]} file đính kèm')
        
        if msg_parts:
            flash(f'✓ Import thành công! Đã nhập: {", ".join(msg_parts)}.', 'success')
        else:
            flash('✓ Import hoàn tất!', 'success')
        return redirect(url_for('export_import'))
    
    except Exception as e:
        import traceback
        print(f"DEBUG: Import error: {str(e)}")
        traceback.print_exc()
        flash(f'Lỗi khi import dữ liệu: {str(e)}', 'danger')
        return redirect(url_for('export_import'))

# ==================== CHAT ROUTES ====================

@app.route('/chat')
@login_required
def chat():
    """Trang chat tổng"""
    # Đếm số users active
    all_users = user_storage.get_all_users()
    total_users = len([u for u in all_users if u['is_active']])
    
    return render_template('chat.html', total_users=total_users)

@app.route('/chat/group/messages')
@login_required
def get_group_messages():
    """API: Lấy tất cả tin nhắn group chat (hoặc phân trang)"""
    # Lấy tham số pagination (nếu có)
    limit = request.args.get('limit', type=int)  # None = lấy tất cả
    offset = request.args.get('offset', default=0, type=int)
    
    # Lấy messages với pagination
    messages = chat_storage.get_all_messages(limit=limit, offset=offset)
    
    # Thêm thông tin sender vào mỗi message
    for msg in messages:
        user = user_storage.get_user_by_id(msg['sender_id'])
        msg['sender_name'] = user.username if user else 'Unknown'
    
    # Lấy tổng số tin nhắn để client biết còn bao nhiêu
    all_messages = chat_storage.get_all_messages()
    total_count = len(all_messages)
    
    return jsonify({
        'success': True,
        'messages': messages,
        'total_count': total_count,
        'has_more': (offset + len(messages)) < total_count
    })

@app.route('/chat/group/send', methods=['POST'])
@login_required
def send_group_message():
    """API: Gửi tin nhắn vào group chat"""
    message = request.form.get('message', '').strip()
    attachment = request.files.get('attachment')
    
    if not message and not attachment:
        return jsonify({'success': False, 'error': 'Tin nhắn hoặc file đính kèm là bắt buộc'}), 400
    
    # Kiểm tra storage limit nếu có file đính kèm
    if attachment and attachment.filename:
        # Đọc file size
        attachment.seek(0, os.SEEK_END)
        file_size = attachment.tell()
        attachment.seek(0)  # Reset về đầu file
        
        # Kiểm tra sender
        can_upload, error_msg = chat_storage.can_upload_file(current_user.id, file_size)
        if not can_upload:
            return jsonify({
                'success': False,
                'error': error_msg,
                'storage_full': True
            }), 400
    
    # Gửi tin nhắn vào group (receiver_id = 0 để đánh dấu là group message)
    try:
        new_message = chat_storage.send_group_message(
            sender_id=current_user.id,
            message=message if message else None,
            attachment_file=attachment if attachment else None
        )
        
        # Emit socket event để realtime update
        try:
            socketio.emit('new_message', {'message': new_message}, broadcast=True)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': new_message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat/group/clear-history', methods=['POST'])
@login_required
def clear_group_chat_history():
    """API: Xóa toàn bộ lịch sử chat tổng (chỉ admin)"""
    # Chỉ admin mới được xóa lịch sử chat tổng
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Chỉ admin mới có quyền xóa lịch sử chat'}), 403
    
    try:
        deleted_count = chat_storage.clear_all_group_messages()
        
        # Log action
        app.logger.info(f"Admin {current_user.username} cleared chat history: {deleted_count} messages deleted")
        
        # Emit socket event để tất cả users refresh
        try:
            socketio.emit('chat_cleared', {}, broadcast=True)
        except:
            pass
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count
        })
    except Exception as e:
        app.logger.error(f"Clear chat history error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat/unread-count')
@login_required
def get_unread_count():
    """API: Lấy số tin nhắn chưa đọc"""
    count = chat_storage.get_unread_count(current_user.id)
    return jsonify({'count': count})

@app.route('/chat/download/<filename>')
@login_required
def download_chat_file(filename):
    """Download file đính kèm trong chat"""
    return send_from_directory(chat_storage.chat_uploads_dir, filename, as_attachment=True)

@app.route('/chat/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_chat_message(message_id):
    """Xóa tin nhắn (chỉ người gửi)"""
    success = chat_storage.delete_message(message_id, current_user.id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Không thể xóa tin nhắn'}), 403

@app.route('/chat/storage-info')
@login_required
def get_storage_info():
    """API: Lấy thông tin storage của user"""
    storage_info = chat_storage.get_storage_info(current_user.id)
    return jsonify(storage_info)

@app.route('/chat/manage-files')
@login_required
def manage_chat_files():
    """Trang quản lý file chat"""
    storage_info = chat_storage.get_storage_info(current_user.id)
    files_list = chat_storage.get_user_files_list(current_user.id)
    
    return render_template('manage_chat_files.html',
                         storage_info=storage_info,
                         files_list=files_list)

@app.route('/chat/clear-history/<int:other_user_id>', methods=['POST'])
@login_required
def clear_chat_history(other_user_id):
    """Xóa lịch sử chat với user (chỉ xóa tin nhắn mà user gửi)"""
    try:
        messages = chat_storage._load_messages()
        
        # Xóa tin nhắn mà current_user gửi cho other_user
        deleted_count = 0
        new_messages = []
        
        for msg in messages:
            if msg['sender_id'] == current_user.id and msg['receiver_id'] == other_user_id:
                # Xóa file đính kèm nếu có
                if msg.get('attachment_filename'):
                    file_path = os.path.join(chat_storage.chat_uploads_dir, msg['attachment_filename'])
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
                deleted_count += 1
            else:
                new_messages.append(msg)
        
        chat_storage._save_messages(new_messages)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== NOTIFICATION ROUTES ====================

@app.route('/notifications')
@login_required
def get_notifications():
    """API: Lấy danh sách thông báo của user"""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', default=50, type=int)
    
    notifications = notification_storage.get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    
    return jsonify({
        'success': True,
        'notifications': notifications
    })

@app.route('/notifications/unread-count')
@login_required
def get_unread_notifications_count():
    """API: Đếm số thông báo chưa đọc"""
    count = notification_storage.get_unread_count(current_user.id)
    return jsonify({
        'success': True,
        'count': count
    })

@app.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """API: Đánh dấu thông báo đã đọc"""
    success = notification_storage.mark_as_read(notification_id, current_user.id)
    return jsonify({'success': success})

@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """API: Đánh dấu tất cả thông báo đã đọc"""
    count = notification_storage.mark_all_as_read(current_user.id)
    return jsonify({
        'success': True,
        'count': count
    })

@app.route('/notifications/create', methods=['POST'])
@login_required
@admin_required
def create_notification():
    """API: Tạo thông báo mới (chỉ admin)"""
    data = request.get_json()
    
    title = data.get('title', '').strip()
    message = data.get('message', '').strip()
    type = data.get('type', 'info')
    user_id = data.get('user_id')  # None = broadcast to all
    link = data.get('link')
    
    if not title or not message:
        return jsonify({
            'success': False,
            'error': 'Tiêu đề và nội dung là bắt buộc'
        }), 400
    
    notification = notification_storage.create_notification(
        title=title,
        message=message,
        type=type,
        user_id=user_id,
        link=link
    )
    
    # Emit socket event để notify realtime
    socketio.emit('new_notification', {
        'notification': notification
    }, broadcast=True)
    
    return jsonify({
        'success': True,
        'notification': notification
    })

@app.route('/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_notification(notification_id):
    """API: Xóa thông báo (chỉ admin)"""
    success = notification_storage.delete_notification(notification_id)
    
    if success:
        # Emit socket event
        socketio.emit('notification_deleted', {
            'notification_id': notification_id
        }, broadcast=True)
    
    return jsonify({'success': success})

if __name__ == '__main__':
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
        sample_note = file_storage.create_note(
            title='Chào mừng!',
            content='Đây là ghi chú đầu tiên của bạn. Bạn có thể chỉnh sửa hoặc xóa nó.',
            category='general'
        )
        
    docs = file_storage.get_all_docs()
    if len(docs) == 0:
        sample_doc = file_storage.create_doc(
            title='Hướng dẫn sử dụng',
            content='''# Hướng dẫn sử dụng hệ thống

## Dashboard
Trang chủ hiển thị tổng quan về số lượng ghi chú và tài liệu, cùng với các mục gần đây.

## Ghi chú (Notes)
Tạo và quản lý các ghi chú cá nhân. Bạn có thể:
- Tạo ghi chú mới
- Chỉnh sửa ghi chú
- Xóa ghi chú
- Tìm kiếm và lọc theo danh mục

## Tài liệu (Documents)
Quản lý tài liệu nội bộ. Tương tự như ghi chú, bạn có thể:
- Tạo tài liệu mới
- Chỉnh sửa tài liệu
- Xóa tài liệu
- Tìm kiếm và lọc theo danh mục

## Tìm kiếm
Sử dụng thanh tìm kiếm để tìm nhanh trong cả ghi chú và tài liệu.

## Lưu trữ
- Người dùng được lưu trong file users.csv
- Ghi chú và tài liệu được lưu dưới dạng file .txt trong thư mục data/
- Danh mục được quản lý bởi admin
''',
            category='hướng dẫn'
        )
    
    # Cấu hình host và port
    HOST = os.environ.get('HOST', '0.0.0.0')  # 0.0.0.0 để truy cập từ mọi IP
    PORT = int(os.environ.get('PORT', 5001))  # Port 5001 để tránh trùng với port 5000
    
    # Hien thi thong tin truy cap
    if DOMAIN_NAME:
        print(f"\n{'='*50}")
        print(f"  Access application at:")
        print(f"  http://{DOMAIN_NAME}:{PORT}")
        if not ':' in DOMAIN_NAME:
            print(f"  http://{DOMAIN_NAME}")
        print(f"{'='*50}\n")
    else:
        print(f"\n{'='*50}")
        print(f"  Access application at:")
        print(f"  http://localhost:{PORT}")
        print(f"  http://127.0.0.1:{PORT}")
        print(f"  http://<your-ip>:{PORT}")
        print(f"  (To use domain, set: set DOMAIN_NAME=yourdomain.com)")
        print(f"{'='*50}\n")
    
    app.run(debug=True, host=HOST, port=PORT)
