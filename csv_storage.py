"""
Module quản lý người dùng bằng CSV
"""
import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

class CSVUserStorage:
    def __init__(self, csv_file='users.csv'):
        self.csv_file = csv_file
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """Đảm bảo file CSV tồn tại với header"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'username', 'email', 'password_hash', 'role', 'created_at', 'is_active'])
    
    def get_next_id(self):
        """Lấy ID tiếp theo"""
        users = self.get_all_users()
        if not users:
            return 1
        return max(int(u['id']) for u in users) + 1
    
    def get_all_users(self):
        """Lấy tất cả users từ CSV"""
        users = []
        if not os.path.exists(self.csv_file):
            return users
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['id'] = int(row['id'])
                row['is_active'] = row['is_active'].lower() == 'true'
                users.append(row)
        return users
    
    def get_user_by_id(self, user_id):
        """Lấy user theo ID"""
        users = self.get_all_users()
        for user in users:
            if user['id'] == int(user_id):
                return self._dict_to_user(user)
        return None
    
    def get_user_by_username(self, username):
        """Lấy user theo username"""
        users = self.get_all_users()
        for user in users:
            if user['username'] == username:
                return self._dict_to_user(user)
        return None
    
    def create_user(self, username, password, email=None, role='user'):
        """Tạo user mới"""
        # Kiểm tra username đã tồn tại
        if self.get_user_by_username(username):
            return None
        
        # Kiểm tra email đã tồn tại (nếu có)
        if email:
            users = self.get_all_users()
            for user in users:
                if user.get('email') and user['email'].lower() == email.lower():
                    return None
        
        user_id = self.get_next_id()
        password_hash = generate_password_hash(password)
        created_at = datetime.utcnow().isoformat()
        
        # Thêm user mới vào CSV
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([user_id, username, email or '', password_hash, role, created_at, 'True'])
        
        return self.get_user_by_id(user_id)
    
    def update_user(self, user_id, username=None, email=None, role=None, password=None, is_active=None):
        """Cập nhật user"""
        users = self.get_all_users()
        updated = False
        
        for user in users:
            if user['id'] == int(user_id):
                if username is not None:
                    # Kiểm tra username trùng (trừ chính nó)
                    existing = self.get_user_by_username(username)
                    if existing and existing.id != int(user_id):
                        return False
                    user['username'] = username
                    updated = True
                
                if email is not None:
                    # Kiểm tra email trùng (trừ chính nó)
                    if email:
                        for u in users:
                            if u.get('email') and u['email'].lower() == email.lower() and u['id'] != int(user_id):
                                return False
                    user['email'] = email or ''
                    updated = True
                
                if role is not None:
                    user['role'] = role
                    updated = True
                
                if password is not None:
                    user['password_hash'] = generate_password_hash(password)
                    updated = True
                
                if is_active is not None:
                    user['is_active'] = is_active
                    updated = True
                
                break
        
        if updated:
            self._save_all_users(users)
        
        return updated
    
    def delete_user(self, user_id):
        """Xóa user"""
        users = self.get_all_users()
        users = [u for u in users if u['id'] != int(user_id)]
        self._save_all_users(users)
        return True
    
    def _save_all_users(self, users):
        """Lưu tất cả users vào CSV"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'username', 'email', 'password_hash', 'role', 'created_at', 'is_active'])
            for user in users:
                writer.writerow([
                    user['id'],
                    user['username'],
                    user.get('email', ''),
                    user['password_hash'],
                    user['role'],
                    user.get('created_at', datetime.utcnow().isoformat()),
                    str(user.get('is_active', True))
                ])
    
    def _dict_to_user(self, user_dict):
        """Chuyển đổi dict thành User object"""
        return User(
            id=user_dict['id'],
            username=user_dict['username'],
            email=user_dict.get('email') or None,
            password_hash=user_dict['password_hash'],
            role=user_dict['role'],
            created_at=datetime.fromisoformat(user_dict.get('created_at', datetime.utcnow().isoformat())) if isinstance(user_dict.get('created_at'), str) else user_dict.get('created_at', datetime.utcnow()),
            is_active=user_dict.get('is_active', True)
        )


class User(UserMixin):
    """User class tương thích với Flask-Login"""
    def __init__(self, id, username, email=None, password_hash=None, role='user', 
                 created_at=None, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow()
        # Lưu is_active vào __dict__ trực tiếp
        self.__dict__['is_active'] = is_active
    
    @property
    def is_active(self):
        """Override property is_active để có thể set"""
        return self.__dict__.get('is_active', True)
    
    @is_active.setter
    def is_active(self, value):
        """Setter cho is_active"""
        self.__dict__['is_active'] = value
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

