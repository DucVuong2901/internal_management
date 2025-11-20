"""
Notification Storage Module
Quản lý thông báo hệ thống
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class NotificationStorage:
    """Lưu trữ và quản lý thông báo"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.notifications_file = os.path.join(data_dir, 'notifications.json')
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Đảm bảo file notifications.json tồn tại"""
        if not os.path.exists(self.notifications_file):
            self._save_notifications([])
    
    def _load_notifications(self) -> List[Dict]:
        """Load tất cả thông báo từ file"""
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_notifications(self, notifications: List[Dict]):
        """Lưu thông báo vào file"""
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
    
    def create_notification(self, title: str, message: str, type: str = 'info', 
                          user_id: Optional[int] = None, link: Optional[str] = None) -> Dict:
        """
        Tạo thông báo mới
        
        Args:
            title: Tiêu đề thông báo
            message: Nội dung thông báo
            type: Loại thông báo (info, success, warning, danger)
            user_id: ID người dùng (None = thông báo toàn hệ thống)
            link: Link liên quan (optional)
        
        Returns:
            Dict chứa thông tin thông báo đã tạo
        """
        notifications = self._load_notifications()
        
        # Tạo ID mới
        new_id = max([n.get('id', 0) for n in notifications], default=0) + 1
        
        notification = {
            'id': new_id,
            'title': title,
            'message': message,
            'type': type,
            'user_id': user_id,  # None = broadcast to all
            'link': link,
            'created_at': datetime.utcnow().isoformat(),
            'read_by': []  # List of user IDs who have read this
        }
        
        notifications.append(notification)
        self._save_notifications(notifications)
        
        return notification
    
    def get_notifications(self, user_id: Optional[int] = None, 
                         unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """
        Lấy danh sách thông báo
        
        Args:
            user_id: ID người dùng (None = lấy thông báo hệ thống)
            unread_only: Chỉ lấy thông báo chưa đọc
            limit: Số lượng thông báo tối đa
        
        Returns:
            List các thông báo
        """
        notifications = self._load_notifications()
        
        # Filter theo user_id
        if user_id is not None:
            # Lấy thông báo của user hoặc thông báo broadcast (user_id = None)
            notifications = [
                n for n in notifications 
                if n.get('user_id') is None or n.get('user_id') == user_id
            ]
        
        # Filter chưa đọc
        if unread_only and user_id is not None:
            notifications = [
                n for n in notifications 
                if user_id not in n.get('read_by', [])
            ]
        
        # Sắp xếp theo thời gian (mới nhất trước)
        notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Limit
        return notifications[:limit]
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Đánh dấu thông báo đã đọc
        
        Args:
            notification_id: ID thông báo
            user_id: ID người dùng
        
        Returns:
            True nếu thành công
        """
        notifications = self._load_notifications()
        
        for notification in notifications:
            if notification['id'] == notification_id:
                if user_id not in notification.get('read_by', []):
                    notification.setdefault('read_by', []).append(user_id)
                    self._save_notifications(notifications)
                return True
        
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """
        Đánh dấu tất cả thông báo đã đọc
        
        Args:
            user_id: ID người dùng
        
        Returns:
            Số lượng thông báo đã đánh dấu
        """
        notifications = self._load_notifications()
        count = 0
        
        for notification in notifications:
            # Chỉ đánh dấu thông báo của user hoặc broadcast
            if notification.get('user_id') is None or notification.get('user_id') == user_id:
                if user_id not in notification.get('read_by', []):
                    notification.setdefault('read_by', []).append(user_id)
                    count += 1
        
        if count > 0:
            self._save_notifications(notifications)
        
        return count
    
    def delete_notification(self, notification_id: int) -> bool:
        """
        Xóa thông báo
        
        Args:
            notification_id: ID thông báo
        
        Returns:
            True nếu thành công
        """
        notifications = self._load_notifications()
        original_count = len(notifications)
        
        notifications = [n for n in notifications if n['id'] != notification_id]
        
        if len(notifications) < original_count:
            self._save_notifications(notifications)
            return True
        
        return False
    
    def get_unread_count(self, user_id: int) -> int:
        """
        Đếm số thông báo chưa đọc
        
        Args:
            user_id: ID người dùng
        
        Returns:
            Số lượng thông báo chưa đọc
        """
        notifications = self.get_notifications(user_id=user_id, unread_only=True)
        return len(notifications)
    
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """
        Xóa thông báo cũ hơn X ngày
        
        Args:
            days: Số ngày
        
        Returns:
            Số lượng thông báo đã xóa
        """
        notifications = self._load_notifications()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        original_count = len(notifications)
        notifications = [
            n for n in notifications
            if datetime.fromisoformat(n.get('created_at', '')) > cutoff_date
        ]
        
        deleted_count = original_count - len(notifications)
        
        if deleted_count > 0:
            self._save_notifications(notifications)
        
        return deleted_count
