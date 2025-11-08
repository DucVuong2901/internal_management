"""
Chat Storage - Lưu trữ tin nhắn chat bằng JSON (tương thích với hệ thống hiện tại)
Sẽ migrate sang database sau
"""
import os
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

class ChatStorage:
    # Storage limit per user: 1GB
    STORAGE_LIMIT_BYTES = 1 * 1024 * 1024 * 1024  # 1GB
    WARNING_THRESHOLD = 0.8  # Cảnh báo khi dùng >80%
    MESSAGE_RETENTION_HOURS = 72  # Tự động xóa tin nhắn sau 72 giờ
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.chat_file = os.path.join(data_dir, 'chat_messages.json')
        self.chat_uploads_dir = os.path.join(data_dir, 'uploads', 'chat')
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.chat_uploads_dir, exist_ok=True)
        
        # Khởi tạo file nếu chưa tồn tại
        if not os.path.exists(self.chat_file):
            self._save_messages([])
        
        # Tự động xóa tin nhắn cũ khi khởi tạo
        self._cleanup_old_messages()
    
    def _load_messages(self):
        """Load messages từ JSON"""
        try:
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_messages(self, messages):
        """Lưu messages vào JSON"""
        with open(self.chat_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    def _cleanup_old_messages(self):
        """Tự động xóa tin nhắn cũ hơn MESSAGE_RETENTION_HOURS giờ"""
        messages = self._load_messages()
        cutoff_time = datetime.utcnow() - timedelta(hours=self.MESSAGE_RETENTION_HOURS)
        
        messages_to_keep = []
        deleted_count = 0
        
        for msg in messages:
            try:
                msg_time = datetime.fromisoformat(msg['created_at'])
                if msg_time >= cutoff_time:
                    messages_to_keep.append(msg)
                else:
                    # Xóa file đính kèm nếu có
                    if msg.get('attachment_filename'):
                        file_path = os.path.join(self.chat_uploads_dir, msg['attachment_filename'])
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except:
                                pass
                    deleted_count += 1
            except:
                # Giữ lại tin nhắn nếu không parse được thời gian
                messages_to_keep.append(msg)
        
        if deleted_count > 0:
            self._save_messages(messages_to_keep)
            print(f"✓ Đã tự động xóa {deleted_count} tin nhắn cũ hơn {self.MESSAGE_RETENTION_HOURS} giờ")
        
        return deleted_count
    
    def get_next_id(self):
        """Lấy ID tiếp theo"""
        messages = self._load_messages()
        if not messages:
            return 1
        return max(msg['id'] for msg in messages) + 1
    
    def send_message(self, sender_id, receiver_id, message=None, attachment_file=None):
        """Gửi tin nhắn"""
        messages = self._load_messages()
        msg_id = self.get_next_id()
        
        attachment_filename = None
        attachment_original_name = None
        
        # Xử lý file đính kèm
        if attachment_file:
            original_name = secure_filename(attachment_file.filename)
            file_ext = os.path.splitext(original_name)[1]
            attachment_filename = f"chat_{msg_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"
            
            # Lưu file
            file_path = os.path.join(self.chat_uploads_dir, attachment_filename)
            attachment_file.save(file_path)
            attachment_original_name = original_name
        
        new_message = {
            'id': msg_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'message': message,
            'attachment_filename': attachment_filename,
            'attachment_original_name': attachment_original_name,
            'is_read': False,
            'created_at': datetime.utcnow().isoformat()
        }
        
        messages.append(new_message)
        self._save_messages(messages)
        
        return new_message
    
    def get_conversation(self, user1_id, user2_id, limit=500):
        """Lấy cuộc hội thoại giữa 2 users"""
        # KHÔNG cleanup ở đây - chỉ cleanup khi khởi tạo app
        # self._cleanup_old_messages()
        
        messages = self._load_messages()
        
        # Lọc tin nhắn giữa 2 users
        conversation = [
            msg for msg in messages
            if (msg['sender_id'] == user1_id and msg['receiver_id'] == user2_id) or
               (msg['sender_id'] == user2_id and msg['receiver_id'] == user1_id)
        ]
        
        # Sắp xếp theo thời gian
        conversation.sort(key=lambda x: x['created_at'])
        
        # Giới hạn số lượng
        return conversation[-limit:]
    
    def get_user_conversations(self, user_id):
        """Lấy danh sách người đã chat với user"""
        messages = self._load_messages()
        
        # Tìm tất cả users đã chat
        users = set()
        for msg in messages:
            if msg['sender_id'] == user_id:
                users.add(msg['receiver_id'])
            elif msg['receiver_id'] == user_id:
                users.add(msg['sender_id'])
        
        # Lấy tin nhắn cuối cùng và số tin chưa đọc cho mỗi user
        conversations = []
        for other_user_id in users:
            conv_messages = self.get_conversation(user_id, other_user_id)
            if conv_messages:
                last_message = conv_messages[-1]
                unread_count = sum(
                    1 for msg in conv_messages
                    if msg['receiver_id'] == user_id and not msg['is_read']
                )
                conversations.append({
                    'user_id': other_user_id,
                    'last_message': last_message,
                    'unread_count': unread_count
                })
        
        # Sắp xếp theo thời gian tin nhắn cuối
        conversations.sort(key=lambda x: x['last_message']['created_at'], reverse=True)
        
        return conversations
    
    def mark_as_read(self, user_id, other_user_id):
        """Đánh dấu tất cả tin nhắn từ other_user là đã đọc"""
        messages = self._load_messages()
        
        for msg in messages:
            if msg['sender_id'] == other_user_id and msg['receiver_id'] == user_id:
                msg['is_read'] = True
        
        self._save_messages(messages)
    
    def get_unread_count(self, user_id):
        """Đếm số tin nhắn chưa đọc của user"""
        messages = self._load_messages()
        
        return sum(
            1 for msg in messages
            if msg['receiver_id'] == user_id and not msg['is_read']
        )
    
    def delete_message(self, message_id, user_id):
        """Xóa tin nhắn (chỉ người gửi mới xóa được)"""
        messages = self._load_messages()
        
        # Tìm message để xóa file đính kèm
        for msg in messages:
            if msg['id'] == message_id and msg['sender_id'] == user_id:
                if msg.get('attachment_filename'):
                    file_path = os.path.join(self.chat_uploads_dir, msg['attachment_filename'])
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
        
        messages = [
            msg for msg in messages
            if not (msg['id'] == message_id and msg['sender_id'] == user_id)
        ]
        
        self._save_messages(messages)
        return True
    
    def get_user_storage_usage(self, user_id):
        """Tính tổng dung lượng file chat của user (bytes)"""
        messages = self._load_messages()
        total_size = 0
        
        for msg in messages:
            # Chỉ tính file của user gửi hoặc nhận
            if msg['sender_id'] == user_id or msg['receiver_id'] == user_id:
                if msg.get('attachment_filename'):
                    file_path = os.path.join(self.chat_uploads_dir, msg['attachment_filename'])
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        
        return total_size
    
    def get_storage_info(self, user_id):
        """Lấy thông tin storage của user"""
        used_bytes = self.get_user_storage_usage(user_id)
        limit_bytes = self.STORAGE_LIMIT_BYTES
        used_percent = (used_bytes / limit_bytes) * 100
        remaining_bytes = limit_bytes - used_bytes
        
        return {
            'used_bytes': used_bytes,
            'used_mb': round(used_bytes / (1024 * 1024), 2),
            'used_gb': round(used_bytes / (1024 * 1024 * 1024), 2),
            'limit_bytes': limit_bytes,
            'limit_gb': 1.0,
            'remaining_bytes': remaining_bytes,
            'remaining_mb': round(remaining_bytes / (1024 * 1024), 2),
            'used_percent': round(used_percent, 2),
            'is_warning': used_percent >= (self.WARNING_THRESHOLD * 100),
            'is_full': used_bytes >= limit_bytes
        }
    
    def can_upload_file(self, user_id, file_size):
        """Kiểm tra user có thể upload file không"""
        storage_info = self.get_storage_info(user_id)
        
        if storage_info['is_full']:
            return False, "Bạn đã dùng hết 1GB dung lượng chat. Vui lòng xóa bớt file hoặc chuyển lên Note."
        
        if storage_info['remaining_bytes'] < file_size:
            remaining_mb = storage_info['remaining_mb']
            needed_mb = round(file_size / (1024 * 1024), 2)
            return False, f"Không đủ dung lượng. Còn {remaining_mb}MB, cần {needed_mb}MB. Vui lòng xóa bớt file."
        
        return True, None
    
    def get_user_files_list(self, user_id):
        """Lấy danh sách file của user để quản lý"""
        messages = self._load_messages()
        files = []
        
        for msg in messages:
            if (msg['sender_id'] == user_id or msg['receiver_id'] == user_id) and msg.get('attachment_filename'):
                file_path = os.path.join(self.chat_uploads_dir, msg['attachment_filename'])
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    files.append({
                        'message_id': msg['id'],
                        'filename': msg['attachment_filename'],
                        'original_name': msg.get('attachment_original_name', msg['attachment_filename']),
                        'size_bytes': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'created_at': msg['created_at'],
                        'sender_id': msg['sender_id'],
                        'receiver_id': msg['receiver_id'],
                        'is_sender': msg['sender_id'] == user_id
                    })
        
        # Sắp xếp theo size giảm dần
        files.sort(key=lambda x: x['size_bytes'], reverse=True)
        
        return files
