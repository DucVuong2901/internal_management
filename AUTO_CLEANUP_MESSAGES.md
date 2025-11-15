# Tự động xóa tin nhắn chat cũ hơn 48 giờ

## Ngày: 15/11/2025

## Tóm tắt

Đã thêm tính năng **tự động xóa tin nhắn chat cũ hơn 48 giờ** để tiết kiệm storage và giữ chat room gọn gàng.

## Cơ chế hoạt động

### 1. **Cleanup khi khởi động app**
```python
# chat_storage.py __init__()
def __init__(self, data_dir='data'):
    # ...
    # Tự động xóa tin nhắn cũ khi khởi tạo
    self._cleanup_old_messages()
```

### 2. **Scheduled cleanup mỗi 6 giờ**
```python
# app.py
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

scheduler = BackgroundScheduler(timezone=utc)

def cleanup_old_chat_messages():
    """Tự động xóa tin nhắn cũ hơn 48 giờ"""
    deleted = chat_storage._cleanup_old_messages()
    if deleted > 0:
        print(f"✓ Scheduled cleanup: Deleted {deleted} old messages")

# Chạy mỗi 6 giờ
scheduler.add_job(
    func=cleanup_old_chat_messages,
    trigger='interval',
    hours=6,
    id='cleanup_chat_messages',
    name='Cleanup old chat messages (>48h)'
)

scheduler.start()
```

### 3. **Logic cleanup**
```python
# chat_storage.py
MESSAGE_RETENTION_HOURS = 48  # 48 giờ

def _cleanup_old_messages(self):
    """Tự động xóa tin nhắn cũ hơn MESSAGE_RETENTION_HOURS giờ"""
    messages = self._load_messages()
    cutoff_time = datetime.utcnow() - timedelta(hours=self.MESSAGE_RETENTION_HOURS)
    
    messages_to_keep = []
    deleted_count = 0
    
    for msg in messages:
        msg_time = datetime.fromisoformat(msg['created_at'])
        if msg_time >= cutoff_time:
            # Giữ lại message mới
            messages_to_keep.append(msg)
        else:
            # Xóa message cũ
            # Xóa file đính kèm nếu có
            if msg.get('attachment_filename'):
                file_path = os.path.join(self.chat_uploads_dir, msg['attachment_filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
            deleted_count += 1
    
    if deleted_count > 0:
        self._save_messages(messages_to_keep)
        print(f"✓ Đã tự động xóa {deleted_count} tin nhắn cũ hơn {self.MESSAGE_RETENTION_HOURS} giờ")
    
    return deleted_count
```

## Timeline

```
┌─────────────────────────────────────────────────────────┐
│  T = 0h: Message được gửi                              │
│  created_at = "2025-11-15T00:00:00"                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  T = 6h: Scheduler check (message < 48h)               │
│  → Giữ lại message                                     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  T = 12h: Scheduler check (message < 48h)              │
│  → Giữ lại message                                     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  T = 48h: Scheduler check (message = 48h)              │
│  → Giữ lại message (vẫn còn trong cutoff)             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  T = 48h + 1 phút: Scheduler check (message > 48h)     │
│  → XÓA message + file đính kèm                         │
└─────────────────────────────────────────────────────────┘
```

## Khi nào cleanup chạy?

### 1. **Khi khởi động app**
```
Server start
  ↓
chat_storage = ChatStorage(data_dir=DATA_DIR)
  ↓
__init__() gọi _cleanup_old_messages()
  ↓
Xóa tất cả messages > 48h
```

### 2. **Mỗi 6 giờ**
```
Scheduler trigger (every 6 hours)
  ↓
cleanup_old_chat_messages()
  ↓
chat_storage._cleanup_old_messages()
  ↓
Xóa tất cả messages > 48h
```

### 3. **Lịch chạy cụ thể**
```
00:00 - Server start → Cleanup
06:00 - Scheduled cleanup
12:00 - Scheduled cleanup
18:00 - Scheduled cleanup
00:00 - Scheduled cleanup (ngày hôm sau)
...
```

## Những gì bị xóa

### ✅ Messages cũ hơn 48 giờ
```json
{
  "id": 123,
  "sender_id": 1,
  "receiver_id": 0,
  "message": "Hello",
  "created_at": "2025-11-13T00:00:00"  // > 48h
}
```

### ✅ File đính kèm của messages cũ
```
data/uploads/chat/chat_123_20251113000000.jpg
```

### ❌ KHÔNG xóa
- Messages mới hơn 48 giờ
- File đính kèm của messages mới

## Logs

### Console output
```
✓ Đã tự động xóa 15 tin nhắn cũ hơn 48 giờ
✓ Scheduler started: Auto cleanup old messages every 6 hours
✓ Scheduled cleanup: Deleted 3 old messages
```

### App logs (data/logs/app.log)
```
[2025-11-15 09:29:35] INFO in app: Scheduled cleanup: Deleted 3 old messages
```

## Configuration

### Thay đổi thời gian retention

Sửa trong `chat_storage.py`:
```python
class ChatStorage:
    MESSAGE_RETENTION_HOURS = 48  # Thay đổi số giờ ở đây
```

Ví dụ:
- `24` = Xóa sau 24 giờ (1 ngày)
- `48` = Xóa sau 48 giờ (2 ngày) ← **Hiện tại**
- `72` = Xóa sau 72 giờ (3 ngày)
- `168` = Xóa sau 168 giờ (7 ngày)

### Thay đổi tần suất cleanup

Sửa trong `app.py`:
```python
scheduler.add_job(
    func=cleanup_old_chat_messages,
    trigger='interval',
    hours=6,  # Thay đổi số giờ ở đây
    # ...
)
```

Ví dụ:
- `hours=1` = Cleanup mỗi 1 giờ
- `hours=6` = Cleanup mỗi 6 giờ ← **Hiện tại**
- `hours=12` = Cleanup mỗi 12 giờ
- `hours=24` = Cleanup mỗi 24 giờ (1 ngày)

### Tắt scheduled cleanup

Nếu muốn chỉ cleanup khi khởi động app:
```python
# Comment out hoặc xóa phần này trong app.py
# scheduler.add_job(...)
# scheduler.start()
```

## Testing

### Test 1: Kiểm tra cleanup khi khởi động
```bash
# Restart server
taskkill /F /IM python.exe
python app.py

# Xem console output
# Kỳ vọng: "✓ Đã tự động xóa X tin nhắn cũ hơn 48 giờ"
```

### Test 2: Kiểm tra scheduled cleanup
```bash
# Đợi 6 giờ hoặc sửa hours=0.1 (6 phút) để test
# Xem console output hoặc logs
# Kỳ vọng: "✓ Scheduled cleanup: Deleted X old messages"
```

### Test 3: Tạo message cũ giả để test
```python
# Tạo script test_cleanup.py
from chat_storage import ChatStorage
from datetime import datetime, timedelta
import json

chat_storage = ChatStorage(data_dir='data')
messages = chat_storage._load_messages()

# Tạo message cũ 50 giờ
old_time = (datetime.utcnow() - timedelta(hours=50)).isoformat()
messages.append({
    'id': 9999,
    'sender_id': 1,
    'receiver_id': 0,
    'message': 'Old test message',
    'created_at': old_time,
    'attachment_filename': None,
    'is_read': False
})

chat_storage._save_messages(messages)
print(f"✓ Created test message with timestamp: {old_time}")

# Chạy cleanup
deleted = chat_storage._cleanup_old_messages()
print(f"✓ Cleanup deleted {deleted} messages")
```

## Dependencies

### APScheduler
```bash
pip install apscheduler
```

Version hiện tại: `3.6.3`

### Pytz
```bash
pip install pytz
```

Được sử dụng để set timezone cho scheduler.

## Monitoring

### Kiểm tra scheduler status
```python
# Trong Python console hoặc route debug
from app import scheduler

# Xem tất cả jobs
print(scheduler.get_jobs())

# Xem job cleanup
job = scheduler.get_job('cleanup_chat_messages')
print(f"Next run: {job.next_run_time}")
```

### Kiểm tra logs
```bash
# Xem logs
cat data/logs/app.log | grep "cleanup"

# Hoặc trên Windows
type data\logs\app.log | findstr "cleanup"
```

## Lợi ích

### 1. **Tiết kiệm storage**
- Tự động xóa messages cũ
- Xóa cả file đính kèm
- Giữ storage ở mức hợp lý

### 2. **Performance tốt hơn**
- Ít messages hơn → Load nhanh hơn
- JSON file nhỏ hơn → Parse nhanh hơn
- Ít files hơn → Backup nhanh hơn

### 3. **Privacy**
- Messages cũ tự động bị xóa
- Không lưu trữ vô thời hạn
- Phù hợp với GDPR/privacy policies

### 4. **Maintenance tự động**
- Không cần manual cleanup
- Chạy background, không ảnh hưởng users
- Reliable với scheduler

## Lưu ý

### ⚠️ Messages bị xóa KHÔNG thể khôi phục
- Backup định kỳ nếu cần giữ lịch sử
- Cân nhắc tăng retention time nếu cần

### ⚠️ Timezone
- Scheduler sử dụng UTC
- Messages created_at cũng là UTC
- Đảm bảo consistency

### ⚠️ Server restart
- Scheduler restart khi server restart
- Job schedule được tính lại từ thời điểm restart
- Không mất jobs đã schedule

## Rollback

Nếu muốn tắt auto cleanup:

### 1. Tắt scheduled cleanup
```python
# app.py - Comment out
# scheduler.add_job(...)
# scheduler.start()
```

### 2. Tắt cleanup khi khởi động
```python
# chat_storage.py __init__()
# Comment out
# self._cleanup_old_messages()
```

### 3. Thay đổi retention time
```python
# chat_storage.py
MESSAGE_RETENTION_HOURS = 168  # 7 ngày thay vì 48 giờ
```

## Server status

**Server đang chạy**: http://127.0.0.1:5001

**Scheduler status**: ✅ Running
**Cleanup interval**: Every 6 hours
**Retention time**: 48 hours

## Kết luận

✅ Đã thêm tính năng tự động xóa tin nhắn cũ hơn 48 giờ
✅ Cleanup chạy khi khởi động app và mỗi 6 giờ
✅ Xóa cả messages và file đính kèm
✅ Có logs để monitoring
✅ Có thể config retention time và cleanup interval
✅ Sẵn sàng sử dụng!
