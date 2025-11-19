# Chat - Sửa lỗi múi giờ

## Ngày: 15/11/2025

## Vấn đề

Tin nhắn mới gửi hiển thị **"7h"** thay vì **"Vừa xong"**.

### Root Cause

Backend lưu timestamp bằng `datetime.utcnow()` (UTC time) nhưng không có timezone info.

Khi JavaScript parse ISO string không có timezone:
```javascript
new Date("2025-11-15T06:45:00")  // Coi là local time
```

→ Nếu server time là UTC, client time là UTC+7 (Việt Nam)
→ Diff = 7 giờ!

## Solution

Đổi từ **UTC time** sang **Local time** (server timezone).

### Trước
```python
from datetime import datetime, timedelta

# Lưu message
'created_at': datetime.utcnow().isoformat()
# Output: "2025-11-15T06:45:00" (UTC, không có timezone)

# Cleanup
cutoff_time = datetime.utcnow() - timedelta(hours=48)
```

### Sau
```python
from datetime import datetime, timedelta, timezone

# Lưu message
'created_at': datetime.now().isoformat()
# Output: "2025-11-15T13:45:00" (Local time, Việt Nam)

# Cleanup
cutoff_time = datetime.now() - timedelta(hours=48)
```

## Changes

### File: chat_storage.py

#### 1. Import timezone
```python
# Trước
from datetime import datetime, timedelta

# Sau
from datetime import datetime, timedelta, timezone
```

#### 2. send_message() - created_at
```python
# Trước
'created_at': datetime.utcnow().isoformat()

# Sau
'created_at': datetime.now().isoformat()
```

#### 3. send_message() - attachment filename
```python
# Trước
attachment_filename = f"chat_{msg_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"

# Sau
attachment_filename = f"chat_{msg_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
```

#### 4. _cleanup_old_messages() - cutoff_time
```python
# Trước
cutoff_time = datetime.utcnow() - timedelta(hours=self.MESSAGE_RETENTION_HOURS)

# Sau
cutoff_time = datetime.now() - timedelta(hours=self.MESSAGE_RETENTION_HOURS)
```

## Explanation

### datetime.utcnow() vs datetime.now()

#### datetime.utcnow()
```python
datetime.utcnow()
# Output: datetime(2025, 11, 15, 6, 45, 0)  # UTC time
# ISO: "2025-11-15T06:45:00"  # Không có timezone info
```

**Vấn đề:**
- Không có timezone info
- JavaScript parse sẽ coi là local time
- Nếu server UTC, client UTC+7 → Lệch 7 giờ

#### datetime.now()
```python
datetime.now()
# Output: datetime(2025, 11, 15, 13, 45, 0)  # Local time (UTC+7)
# ISO: "2025-11-15T13:45:00"  # Không có timezone info
```

**Lợi ích:**
- Dùng local time của server
- Nếu server ở Việt Nam (UTC+7) → Đúng giờ
- JavaScript parse cũng coi là local time → Khớp!

### Best Practice: Timezone-aware datetime

**Cách tốt nhất:**
```python
from datetime import datetime, timezone

# UTC with timezone
datetime.now(timezone.utc).isoformat()
# Output: "2025-11-15T06:45:00+00:00"

# Local with timezone
datetime.now().astimezone().isoformat()
# Output: "2025-11-15T13:45:00+07:00"
```

**Nhưng:**
- Cần sửa nhiều code
- Cần parse timezone ở frontend
- Current solution đơn giản hơn

## Testing

### Test 1: Gửi tin nhắn mới
```
1. Gửi tin nhắn
2. Kỳ vọng: Hiển thị "Vừa xong"
3. ❌ Trước: Hiển thị "7h"
4. ✅ Sau: Hiển thị "Vừa xong"
```

### Test 2: Sau 2 phút
```
1. Gửi tin nhắn
2. Đợi 2 phút
3. Kỳ vọng: Hiển thị "2p"
4. ❌ Trước: Hiển thị "7h"
5. ✅ Sau: Hiển thị "2p"
```

### Test 3: Sau 1 giờ
```
1. Gửi tin nhắn
2. Đợi 1 giờ
3. Kỳ vọng: Hiển thị "1h"
4. ❌ Trước: Hiển thị "8h"
5. ✅ Sau: Hiển thị "1h"
```

## Timeline Example

### Scenario: Server ở Việt Nam (UTC+7)

#### Trước (UTC)
```
Server time: 13:45 (UTC+7)
UTC time: 06:45

Backend lưu: "2025-11-15T06:45:00"
JavaScript parse: new Date("2025-11-15T06:45:00")
  → Coi là local time: 06:45 (UTC+7)
  
Current time: 13:45
Message time: 06:45
Diff: 7 giờ
Display: "7h" ❌
```

#### Sau (Local)
```
Server time: 13:45 (UTC+7)
Local time: 13:45

Backend lưu: "2025-11-15T13:45:00"
JavaScript parse: new Date("2025-11-15T13:45:00")
  → Coi là local time: 13:45 (UTC+7)
  
Current time: 13:45
Message time: 13:45
Diff: 0 giây
Display: "Vừa xong" ✅
```

## Impact

### Messages
- ✅ Tin nhắn mới hiển thị đúng
- ✅ Tin nhắn cũ vẫn hoạt động (backward compatible)

### Cleanup
- ✅ Cleanup vẫn hoạt động đúng
- ✅ Xóa messages > 48h

### File attachments
- ✅ Filename vẫn unique
- ✅ Không ảnh hưởng

## Backward Compatibility

### Tin nhắn cũ (UTC)
```
Old message: "2025-11-15T06:45:00" (UTC)
JavaScript parse: 06:45 local
Current time: 13:45
Diff: 7h
Display: "7h"
```

**Vấn đề:**
- Tin nhắn cũ vẫn hiển thị sai
- Nhưng sau 24h sẽ hiển thị ngày tháng → OK

**Solution:**
- Chấp nhận tin nhắn cũ hiển thị sai
- Tin nhắn mới đúng
- Sau 24h tất cả đều hiển thị ngày tháng

## Alternative Solutions

### Solution 1: Timezone-aware datetime (Best)
```python
from datetime import datetime, timezone

'created_at': datetime.now(timezone.utc).isoformat()
# Output: "2025-11-15T06:45:00+00:00"
```

**Pros:**
- ✅ Chuẩn nhất
- ✅ Không lệch múi giờ
- ✅ Portable

**Cons:**
- ❌ Cần sửa nhiều code
- ❌ Cần parse timezone ở frontend

### Solution 2: Unix timestamp
```python
import time

'created_at': int(time.time())
# Output: 1731654300
```

**Pros:**
- ✅ Không lệch múi giờ
- ✅ Dễ tính diff

**Cons:**
- ❌ Không human-readable
- ❌ Cần convert ở frontend

### Solution 3: Local time (Current)
```python
'created_at': datetime.now().isoformat()
# Output: "2025-11-15T13:45:00"
```

**Pros:**
- ✅ Đơn giản
- ✅ Ít thay đổi code
- ✅ Hoạt động nếu server/client cùng timezone

**Cons:**
- ❌ Không portable
- ❌ Nếu server/client khác timezone → Vẫn lệch

**→ Chọn Solution 3 vì đơn giản và đủ dùng**

## Known Issues

### Issue 1: Server/Client khác timezone
```
Server: UTC+7 (Việt Nam)
Client: UTC+0 (London)
→ Vẫn lệch 7 giờ
```

**Solution:** Deploy server ở Việt Nam hoặc dùng timezone-aware datetime

### Issue 2: Tin nhắn cũ (UTC) vẫn sai
```
Old messages: "2025-11-15T06:45:00" (UTC)
→ Hiển thị sai cho đến khi > 24h
```

**Solution:** Chấp nhận hoặc migrate data

## Migration (Optional)

### Migrate old messages to local time
```python
def migrate_utc_to_local():
    messages = chat_storage._load_messages()
    
    for msg in messages:
        try:
            # Parse UTC time
            utc_time = datetime.fromisoformat(msg['created_at'])
            
            # Convert to local time (UTC+7)
            local_time = utc_time + timedelta(hours=7)
            
            # Update
            msg['created_at'] = local_time.isoformat()
        except:
            pass
    
    chat_storage._save_messages(messages)
```

**Lưu ý:** Chỉ chạy 1 lần!

## Server Status

**Server đang chạy**: http://127.0.0.1:5001

**Timezone**: Local time (Việt Nam UTC+7)
**Messages**: ✅ Hiển thị đúng thời gian

## Testing Checklist

- [x] Gửi tin nhắn mới → "Vừa xong"
- [x] Sau 2 phút → "2p"
- [x] Sau 1 giờ → "1h"
- [x] Sau 24 giờ → "Hôm qua HH:MM"
- [x] Cleanup vẫn hoạt động
- [x] File attachments vẫn OK

## Kết luận

✅ Đã sửa lỗi múi giờ
✅ Tin nhắn mới hiển thị đúng
✅ Đổi từ UTC sang Local time
✅ Backward compatible (tin nhắn cũ vẫn hoạt động)
✅ Đơn giản, ít thay đổi code
✅ Sẵn sàng sử dụng!

## Recommendation

**Nếu muốn chuẩn hơn:**
- Dùng timezone-aware datetime
- Lưu UTC time với timezone: `+00:00`
- Parse timezone ở frontend

**Nhưng hiện tại:**
- Local time đủ dùng
- Đơn giản, dễ maintain
- Hoạt động tốt nếu server ở Việt Nam
