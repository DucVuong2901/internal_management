"""
Migration Script: Chuyển dữ liệu từ CSV/JSON sang Database
KHÔNG XÓA dữ liệu cũ - chỉ copy sang database

Cách sử dụng:
    python migrate_to_database.py

Sau khi chạy xong:
    - Dữ liệu cũ vẫn còn trong thư mục data/
    - Dữ liệu mới trong database.db
    - Có thể rollback bằng cách xóa database.db và dùng lại CSV/JSON
"""
import os
import sys
import json
import csv
from datetime import datetime
from flask import Flask
from models import db, User, Category, Note, Document, Attachment, EditLog

# Setup Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'migration-key'

db.init_app(app)

DATA_DIR = 'data'
USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
METADATA_JSON = os.path.join(DATA_DIR, 'metadata.json')
CATEGORIES_JSON = os.path.join(DATA_DIR, 'categories.json')
EDIT_LOGS_JSON = os.path.join(DATA_DIR, 'edit_logs.json')
NOTES_DIR = os.path.join(DATA_DIR, 'notes')
DOCS_DIR = os.path.join(DATA_DIR, 'docs')


def migrate_users():
    """Migrate users từ CSV sang database"""
    print("\n📊 Migrating Users...")
    
    if not os.path.exists(USERS_CSV):
        print("⚠️  users.csv không tồn tại, bỏ qua")
        return
    
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # Check if user already exists
            existing = User.query.filter_by(username=row['username']).first()
            if existing:
                print(f"   ⏭️  User '{row['username']}' đã tồn tại, bỏ qua")
                continue
            
            user = User(
                id=int(row['id']),
                username=row['username'],
                email=row.get('email') or None,
                password_hash=row['password_hash'],
                role=row.get('role', 'user'),
                is_active=row.get('is_active', 'True').lower() == 'true',
                created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.utcnow()
            )
            db.session.add(user)
            count += 1
        
        db.session.commit()
        print(f"✅ Đã migrate {count} users")


def migrate_categories():
    """Migrate categories từ JSON sang database"""
    print("\n📁 Migrating Categories...")
    
    if not os.path.exists(CATEGORIES_JSON):
        print("⚠️  categories.json không tồn tại, bỏ qua")
        return
    
    with open(CATEGORIES_JSON, 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    count = 0
    for key, cat_data in categories_data.items():
        # Check if category already exists
        existing = Category.query.filter_by(key=key).first()
        if existing:
            print(f"   ⏭️  Category '{key}' đã tồn tại, bỏ qua")
            continue
        
        category = Category(
            key=key,
            name=cat_data.get('name', key),
            display_name=cat_data.get('display_name', cat_data.get('name', key)),
            parent_key=cat_data.get('parent')
        )
        db.session.add(category)
        count += 1
    
    db.session.commit()
    print(f"✅ Đã migrate {count} categories")


def migrate_notes():
    """Migrate notes từ file text + metadata.json sang database"""
    print("\n📝 Migrating Notes...")
    
    if not os.path.exists(METADATA_JSON):
        print("⚠️  metadata.json không tồn tại, bỏ qua")
        return
    
    with open(METADATA_JSON, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    notes_data = metadata.get('notes', [])
    count = 0
    
    for note_meta in notes_data:
        note_id = note_meta['id']
        
        # Check if note already exists
        existing = Note.query.get(note_id)
        if existing:
            print(f"   ⏭️  Note {note_id} đã tồn tại, bỏ qua")
            continue
        
        # Read note content from file
        note_file = os.path.join(NOTES_DIR, f"{note_id}.txt")
        if not os.path.exists(note_file):
            print(f"   ⚠️  File note {note_id}.txt không tồn tại, bỏ qua")
            continue
        
        with open(note_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get category key (handle old format)
        category_key = note_meta.get('category', 'general')
        
        note = Note(
            id=note_id,
            title=note_meta['title'],
            content=content,
            category_key=category_key,
            user_id=note_meta.get('user_id'),
            updated_by=note_meta.get('updated_by'),
            view_count=note_meta.get('view_count', 0),
            created_at=datetime.fromisoformat(note_meta['created_at']),
            updated_at=datetime.fromisoformat(note_meta['updated_at'])
        )
        db.session.add(note)
        
        # Migrate attachments
        for att_data in note_meta.get('attachments', []):
            attachment = Attachment(
                filename=att_data['filename'],
                original_filename=att_data.get('original_filename', att_data['filename']),
                file_type='note',
                note_id=note_id,
                uploaded_at=datetime.fromisoformat(att_data['uploaded_at']) if att_data.get('uploaded_at') else datetime.utcnow()
            )
            db.session.add(attachment)
        
        count += 1
    
    db.session.commit()
    print(f"✅ Đã migrate {count} notes")


def migrate_documents():
    """Migrate documents từ file text + metadata.json sang database"""
    print("\n📄 Migrating Documents...")
    
    if not os.path.exists(METADATA_JSON):
        print("⚠️  metadata.json không tồn tại, bỏ qua")
        return
    
    with open(METADATA_JSON, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    docs_data = metadata.get('docs', [])
    count = 0
    
    for doc_meta in docs_data:
        doc_id = doc_meta['id']
        
        # Check if document already exists
        existing = Document.query.get(doc_id)
        if existing:
            print(f"   ⏭️  Document {doc_id} đã tồn tại, bỏ qua")
            continue
        
        # Read document content from file
        doc_file = os.path.join(DOCS_DIR, f"{doc_id}.txt")
        if not os.path.exists(doc_file):
            print(f"   ⚠️  File document {doc_id}.txt không tồn tại, bỏ qua")
            continue
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get category key (handle old format)
        category_key = doc_meta.get('category', 'general')
        
        document = Document(
            id=doc_id,
            title=doc_meta['title'],
            content=content,
            category_key=category_key,
            user_id=doc_meta.get('user_id'),
            updated_by=doc_meta.get('updated_by'),
            created_at=datetime.fromisoformat(doc_meta['created_at']),
            updated_at=datetime.fromisoformat(doc_meta['updated_at'])
        )
        db.session.add(document)
        
        # Migrate attachments
        for att_data in doc_meta.get('attachments', []):
            attachment = Attachment(
                filename=att_data['filename'],
                original_filename=att_data.get('original_filename', att_data['filename']),
                file_type='doc',
                document_id=doc_id,
                uploaded_at=datetime.fromisoformat(att_data['uploaded_at']) if att_data.get('uploaded_at') else datetime.utcnow()
            )
            db.session.add(attachment)
        
        count += 1
    
    db.session.commit()
    print(f"✅ Đã migrate {count} documents")


def migrate_edit_logs():
    """Migrate edit logs từ JSON sang database"""
    print("\n📋 Migrating Edit Logs...")
    
    if not os.path.exists(EDIT_LOGS_JSON):
        print("⚠️  edit_logs.json không tồn tại, bỏ qua")
        return
    
    with open(EDIT_LOGS_JSON, 'r', encoding='utf-8') as f:
        logs_data = json.load(f)
    
    count = 0
    for log_data in logs_data:
        edit_log = EditLog(
            item_type=log_data['item_type'],
            item_id=log_data['item_id'],
            action=log_data['action'],
            user_id=log_data['user_id'],
            changes=log_data.get('changes'),
            timestamp=datetime.fromisoformat(log_data['timestamp'])
        )
        db.session.add(edit_log)
        count += 1
    
    db.session.commit()
    print(f"✅ Đã migrate {count} edit logs")


def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 MIGRATION: CSV/JSON → Database")
    print("=" * 60)
    print("\n⚠️  LƯU Ý:")
    print("   - Dữ liệu cũ KHÔNG bị xóa")
    print("   - Có thể rollback bằng cách xóa database.db")
    print("   - Nên backup thư mục data/ trước khi migrate")
    print("\n")
    
    response = input("Bạn có muốn tiếp tục? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Đã hủy migration")
        return
    
    with app.app_context():
        # Create all tables
        print("\n🔨 Tạo database schema...")
        db.create_all()
        print("✅ Database schema đã được tạo")
        
        # Run migrations
        try:
            migrate_users()
            migrate_categories()
            migrate_notes()
            migrate_documents()
            migrate_edit_logs()
            
            print("\n" + "=" * 60)
            print("✅ MIGRATION HOÀN TẤT!")
            print("=" * 60)
            print("\n📊 Thống kê:")
            print(f"   Users: {User.query.count()}")
            print(f"   Categories: {Category.query.count()}")
            print(f"   Notes: {Note.query.count()}")
            print(f"   Documents: {Document.query.count()}")
            print(f"   Attachments: {Attachment.query.count()}")
            print(f"   Edit Logs: {EditLog.query.count()}")
            print("\n📁 Database location: data/database.db")
            print("\n🔄 Bước tiếp theo:")
            print("   1. Kiểm tra dữ liệu trong database")
            print("   2. Cập nhật app.py để sử dụng database")
            print("   3. Test kỹ trước khi deploy")
            print("   4. Backup dữ liệu cũ để an toàn")
            
        except Exception as e:
            print(f"\n❌ LỖI: {str(e)}")
            print("Migration thất bại, rollback...")
            db.session.rollback()
            raise


if __name__ == '__main__':
    main()
