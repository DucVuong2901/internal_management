"""
SQLAlchemy Models cho Internal Management System
Chuyển đổi từ CSV/JSON sang Database
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Model cho User"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, editor, user, viewer
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('Note', backref='author', lazy='dynamic', foreign_keys='Note.user_id')
    documents = db.relationship('Document', backref='author', lazy='dynamic', foreign_keys='Document.user_id')
    edit_logs = db.relationship('EditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Model cho Category"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Unique key: "parent/child" hoặc "category"
    name = db.Column(db.String(100), nullable=False)  # Tên hiển thị
    display_name = db.Column(db.String(100), nullable=False)
    parent_key = db.Column(db.String(255), db.ForeignKey('categories.key'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Self-referential relationship
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[key]), lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.key}>'


class Note(db.Model):
    """Model cho Note"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_key = db.Column(db.String(255), db.ForeignKey('categories.key'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = db.relationship('Category', backref='notes', foreign_keys=[category_key])
    attachments = db.relationship('Attachment', backref='note', lazy='dynamic', cascade='all, delete-orphan')
    updater = db.relationship('User', foreign_keys=[updated_by])
    
    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'


class Document(db.Model):
    """Model cho Document"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_key = db.Column(db.String(255), db.ForeignKey('categories.key'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = db.relationship('Category', backref='documents', foreign_keys=[category_key])
    attachments = db.relationship('Attachment', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    updater = db.relationship('User', foreign_keys=[updated_by])
    
    def __repr__(self):
        return f'<Document {self.id}: {self.title}>'


class Attachment(db.Model):
    """Model cho Attachment (file đính kèm)"""
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Tên file lưu trên server
    original_filename = db.Column(db.String(255), nullable=False)  # Tên file gốc
    file_type = db.Column(db.String(10), nullable=False)  # 'note' hoặc 'doc'
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Attachment {self.original_filename}>'


class EditLog(db.Model):
    """Model cho Edit Log"""
    __tablename__ = 'edit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(20), nullable=False, index=True)  # 'note', 'doc', 'user'
    item_id = db.Column(db.Integer, nullable=False, index=True)
    action = db.Column(db.String(20), nullable=False)  # 'create', 'edit', 'delete'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changes = db.Column(db.Text, nullable=True)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<EditLog {self.item_type}:{self.item_id} by User:{self.user_id}>'


class ChatMessage(db.Model):
    """Model cho Chat Message"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=True)  # Text message
    attachment_filename = db.Column(db.String(255), nullable=True)  # File đính kèm
    attachment_original_name = db.Column(db.String(255), nullable=True)  # Tên file gốc
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def __repr__(self):
        return f'<ChatMessage from:{self.sender_id} to:{self.receiver_id}>'
