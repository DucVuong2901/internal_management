from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, session, send_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
import json
import os
import re
import zipfile
import shutil
import tempfile

# Import custom storage modules
from csv_storage import CSVUserStorage, User
from file_storage import FileStorage, Note, Document

# Đảm bảo Flask tìm đúng thư mục templates và static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Cấu hình session để KHÔNG lưu - tự động logout khi đóng tab/trình duyệt (bảo mật cao)
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60  # 1 giờ (session ngắn)
app.config['SESSION_COOKIE_SECURE'] = False  # True nếu dùng HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# QUAN TRỌNG: Cookie chỉ tồn tại trong phiên trình duyệt (KHÔNG persist)
# Không set SESSION_COOKIE_PERMANENT hoặc set = False để cookie tự xóa khi đóng tab
app.config['SESSION_COOKIE_NAME'] = 'session'

# Cấu hình tên miền (có thể set qua environment variable)
# Ví dụ: set DOMAIN_NAME=mydomain.com hoặc DOMAIN_NAME=192.168.1.100
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', None)

# Data directory - Tất cả dữ liệu được lưu ở đây để dễ backup
DATA_DIR = os.path.join(BASE_DIR, 'data')

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

def load_categories():
    """Load categories từ file JSON"""
    if not os.path.exists(categories_file):
        # Tạo categories mặc định
        default_categories = ['general', 'công việc', 'cá nhân', 'học tập', 'quan trọng', 'hướng dẫn']
        save_categories(default_categories)
        return default_categories
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return ['general']

def save_categories(categories):
    """Lưu categories vào file JSON"""
    os.makedirs(os.path.dirname(categories_file), exist_ok=True)
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

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
            # Đăng nhập KHÔNG lưu session - tự động logout khi đóng tab/trình duyệt (bảo mật)
            # remember=False: không lưu cookie persistent
            login_user(user, remember=False)
            # KHÔNG đặt permanent - session chỉ tồn tại trong phiên trình duyệt
            session.permanent = False
            next_page = request.args.get('next')
            flash(f'Chào mừng, {user.username}!', 'success')
            response = redirect(next_page) if next_page else redirect(url_for('dashboard'))
            return response
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # Xóa session và cookie ngay lập tức
    logout_user()
    session.clear()  # Xóa toàn bộ session
    flash('Bạn đã đăng xuất thành công.', 'success')
    response = redirect(url_for('login'))
    # Đảm bảo xóa cookie session
    response.set_cookie('session', '', expires=0, max_age=0)
    return response

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
def check_session_validity():
    """Kiểm tra session còn hiệu lực không - force logout nếu cần"""
    # Kiểm tra xem có header X-Requested-With để biết request từ đâu
    # Nếu session không có key quan trọng, có thể là session cũ
    
    if current_user.is_authenticated:
        # Đảm bảo session không permanent
        session.permanent = False
        
        # Kiểm tra nếu session không có thông tin user, logout
        if '_user_id' not in session and not hasattr(session, '_user_id'):
            # Session không hợp lệ, logout ngay
            logout_user()
            session.clear()
            flash('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'info')
            return redirect(url_for('login'))

@app.after_request
def set_no_cache_headers(response):
    """Thiết lập headers để không cache trang (bảo mật)"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # QUAN TRỌNG: Đảm bảo session cookie không có expires/max-age
    # Để cookie chỉ tồn tại trong phiên trình duyệt (tự xóa khi đóng tab)
    if 'Set-Cookie' in response.headers:
        import re
        cookies = response.headers.getlist('Set-Cookie')
        new_cookies = []
        for cookie in cookies:
            # Nếu là session cookie, loại bỏ expires và Max-Age
            if 'session=' in cookie:
                # Loại bỏ expires và Max-Age để cookie chỉ là session cookie
                cookie = re.sub(r';\s*[Ee]xpires=[^;]+', '', cookie)
                cookie = re.sub(r';\s*[Mm]ax-[Aa]ge=[^;]+', '', cookie)
            new_cookies.append(cookie)
        
        # Cập nhật lại Set-Cookie headers
        response.headers.pop('Set-Cookie', None)
        for cookie in new_cookies:
            response.headers.add('Set-Cookie', cookie)
    
    return response

@app.route('/')
@login_required
def dashboard():
    all_notes = file_storage.get_all_notes()
    all_docs = file_storage.get_all_docs()
    
    notes_count = len(all_notes)
    docs_count = len(all_docs)
    
    # Sắp xếp notes theo view_count (ưu tiên note được xem nhiều nhất), sau đó theo updated_at
    all_notes_sorted = sorted(all_notes, key=lambda x: (x.view_count if hasattr(x, 'view_count') else 0, x.updated_at), reverse=True)
    recent_notes = all_notes_sorted[:5]
    
    recent_docs = all_docs[:5]
    
    return render_template('dashboard.html', 
                         notes_count=notes_count,
                         docs_count=docs_count,
                         recent_notes=recent_notes,
                         recent_docs=recent_docs)

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

@app.route('/notes')
@login_required
def notes():
    category = request.args.get('category', 'all')
    search_query = request.args.get('search', '')
    
    notes_list = file_storage.get_all_notes(category=category, search_query=search_query)
    categories = file_storage.get_note_categories()
    
    return render_template('notes.html', 
                         notes=notes_list,
                         categories=categories,
                         current_category=category,
                         search_query=search_query)

@app.route('/notes/new', methods=['GET', 'POST'])
@can_create_required
def new_note():
    categories = load_categories()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'general')
        
        # Kiểm tra title không rỗng (loại bỏ HTML tags để kiểm tra)
        title_text_only = re.sub(r'<[^>]+>', '', title).strip()
        if not title_text_only:
            flash('Tiêu đề không được để trống!', 'danger')
            return render_template('note_form.html', categories=categories)
        
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
            return render_template('note_form.html', categories=categories)
        if note:
            # Xử lý file đính kèm
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if file_storage.add_note_attachment(note.id, file):
                            pass  # File đã được lưu
            
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
            flash('✓ Đã lưu ghi chú thành công!', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Có lỗi xảy ra khi tạo ghi chú!', 'danger')
    return render_template('note_form.html', categories=categories)

@app.route('/notes/<int:id>/edit', methods=['GET', 'POST'])
@can_edit_required
def edit_note(id):
    note = file_storage.get_note(id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    categories = load_categories()
    
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
            return render_template('note_form.html', note=note, categories=categories)
        
        # Kiểm tra category có trong danh sách được phép
        if category not in categories:
            category = old_category
            flash('Danh mục không hợp lệ, giữ nguyên danh mục cũ.', 'warning')
        
        # Lưu thay đổi trước khi update
        changes = {
            'title': {'old': old_title, 'new': title},
            'content': {'old': note.content[:100] + '...' if len(note.content) > 100 else note.content, 'new': content[:100] + '...' if len(content) > 100 else content},
            'category': {'old': old_category, 'new': category}
        }
        
        try:
            success = file_storage.update_note(
                id,
                title=title,
                content=content,
                category=category
            )
        except Exception as e:
            flash(f'Có lỗi xảy ra khi cập nhật ghi chú: {str(e)}', 'danger')
            return render_template('note_form.html', note=note, categories=categories)
        
        if success:
            # Xử lý file đính kèm mới
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if file_storage.add_note_attachment(id, file):
                            pass  # File đã được lưu
            
            # Tạo log với thông tin chi tiết
            save_edit_log({
                'item_type': 'note',
                'item_id': id,
                'action': 'edit',
                'user_id': current_user.id,
                'changes': json.dumps(changes)
            })
            flash('✓ Đã lưu ghi chú thành công!', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Có lỗi xảy ra khi cập nhật!', 'danger')
    
    return render_template('note_form.html', note=note, categories=categories)

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

@app.route('/notes/<int:note_id>/attachment/<filename>')
@login_required
def download_attachment(note_id, filename):
    """Download hoặc xem file đính kèm"""
    note = file_storage.get_note(note_id)
    if not note:
        flash('Ghi chú không tồn tại!', 'danger')
        return redirect(url_for('notes'))
    
    # Kiểm tra file có thuộc note này không
    # attachments là list of dict, cần truy cập đúng cách
    attachment_exists = any(
        (att.get('filename') if isinstance(att, dict) else getattr(att, 'filename', None)) == filename 
        for att in note.attachments
    )
    if not attachment_exists:
        flash('File không tồn tại!', 'danger')
        return redirect(url_for('view_note', id=note_id))
    
    # Nếu là hình ảnh, hiển thị trong browser, không force download
    is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
    
    return send_from_directory(
        file_storage.notes_uploads_dir,
        filename,
        as_attachment=not is_image  # Force download nếu không phải hình ảnh
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
    
    return render_template('docs.html',
                         docs=docs_list,
                         categories=categories,
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
            'content': {'old': doc.content[:100] + '...' if len(doc.content) > 100 else doc.content, 'new': content[:100] + '...' if len(content) > 100 else content},
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
            
            # Tạo log với thông tin chi tiết
            save_edit_log({
                'item_type': 'doc',
                'item_id': id,
                'action': 'edit',
                'user_id': current_user.id,
                'changes': json.dumps(changes)
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
    
    # Kiểm tra file có thuộc doc này không
    attachment_exists = any(
        (att.get('filename') if isinstance(att, dict) else getattr(att, 'filename', None)) == filename 
        for att in doc.attachments
    )
    if not attachment_exists:
        flash('File không tồn tại!', 'danger')
        return redirect(url_for('view_doc', id=doc_id))
    
    # Nếu là hình ảnh, hiển thị trong browser, không force download
    is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
    
    return send_from_directory(
        file_storage.docs_uploads_dir,
        filename,
        as_attachment=not is_image  # Force download nếu không phải hình ảnh
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

@app.route('/api/check_session')
@login_required
def api_check_session():
    """API endpoint để kiểm tra session còn hiệu lực không"""
    # Nếu đến được đây nghĩa là session còn hợp lệ (vì đã pass @login_required)
    return jsonify({'valid': True, 'username': current_user.username}), 200

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
    if category:
        categories = load_categories()
        if category not in categories:
            categories.append(category)
            save_categories(categories)
            flash(f'Danh mục "{category}" đã được thêm!', 'success')
        else:
            flash(f'Danh mục "{category}" đã tồn tại!', 'warning')
    else:
        flash('Tên danh mục không được để trống!', 'danger')
    return redirect(url_for('manage_categories'))

@app.route('/admin/categories/delete', methods=['POST'])
@admin_required
def delete_category():
    category = request.form.get('category', '').strip().lower()
    if category and category != 'general':
        categories = load_categories()
        if category in categories:
            categories.remove(category)
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
    logs = load_edit_logs()
    
    # Convert created_at từ string sang datetime và xử lý logs
    for log in logs:
        # Convert created_at từ ISO string sang datetime object
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
    
    # Hiển thị thông tin truy cập
    if DOMAIN_NAME:
        print(f"\n{'='*50}")
        print(f"  Truy cập ứng dụng tại:")
        print(f"  http://{DOMAIN_NAME}:{PORT}")
        if not ':' in DOMAIN_NAME:
            print(f"  http://{DOMAIN_NAME}")
        print(f"{'='*50}\n")
    else:
        print(f"\n{'='*50}")
        print(f"  Truy cập ứng dụng tại:")
        print(f"  http://localhost:{PORT}")
        print(f"  http://127.0.0.1:{PORT}")
        print(f"  http://<your-ip>:{PORT}")
        print(f"  (Để dùng tên miền, set: set DOMAIN_NAME=yourdomain.com)")
        print(f"{'='*50}\n")
    
    app.run(debug=True, host=HOST, port=PORT)
