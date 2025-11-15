# Tính năng Xóa lịch sử chat

## Ngày: 15/11/2025

## Tóm tắt

Đã thêm nút **"Xóa lịch sử chat"** vào dropdown menu trong chat tổng. Chỉ **admin** mới có quyền xóa toàn bộ lịch sử chat.

## UI Changes

### Dropdown Menu
```html
<ul class="dropdown-menu dropdown-menu-end">
  <li><a class="dropdown-item" href="#" onclick="showImages()">
    <i class="bi bi-images text-primary"></i> Xem ảnh đã gửi
  </a></li>
  <li><a class="dropdown-item" href="#" onclick="showAttachments()">
    <i class="bi bi-paperclip text-info"></i> Xem file đính kèm
  </a></li>
  <li><hr class="dropdown-divider"></li>
  <li><a class="dropdown-item text-danger" href="#" onclick="clearChatHistory()">
    <i class="bi bi-trash"></i> Xóa lịch sử chat
  </a></li>
</ul>
```

### Vị trí nút
```
┌────────────────────────────────────┐
│  Chat Tổng (5 thành viên)    [⋮]  │ ← Click dropdown
├────────────────────────────────────┤
│  Dropdown Menu:                    │
│  📷 Xem ảnh đã gửi                 │
│  📎 Xem file đính kèm              │
│  ─────────────────                 │
│  🗑️ Xóa lịch sử chat (đỏ)         │ ← Nút mới
└────────────────────────────────────┘
```

## Frontend (chat.html)

### JavaScript Function
```javascript
async function clearChatHistory(){
  // Confirm dialog
  if(!confirm('Xóa toàn bộ lịch sử chat?\n\nHành động này không thể hoàn tác!\n\nTất cả tin nhắn và file đính kèm sẽ bị xóa vĩnh viễn.')){
    return;
  }
  
  try{
    // Gọi API
    const r=await fetch('/chat/group/clear-history',{method:'POST'});
    const d=await r.json();
    
    if(d.success){
      alert('✓ Đã xóa lịch sử chat!');
      lastMessageCount=0;
      document.getElementById('chatMessages').innerHTML='';
      loadMessages();
    }else{
      alert('✗ Lỗi: '+(d.error||'Không thể xóa lịch sử'));
    }
  }catch(e){
    alert('✗ Lỗi kết nối: '+e.message);
  }
}
```

### Socket Event Listener
```javascript
socket.on('chat_cleared',()=>{
  lastMessageCount=0;
  document.getElementById('chatMessages').innerHTML='';
  alert('⚠️ Lịch sử chat đã bị xóa bởi admin');
});
```

## Backend (app.py)

### Route
```python
@app.route('/chat/group/clear-history', methods=['POST'])
@login_required
def clear_group_chat_history():
    """API: Xóa toàn bộ lịch sử chat tổng (chỉ admin)"""
    # Chỉ admin mới được xóa lịch sử chat tổng
    if current_user.role != 'admin':
        return jsonify({
            'success': False, 
            'error': 'Chỉ admin mới có quyền xóa lịch sử chat'
        }), 403
    
    try:
        deleted_count = chat_storage.clear_all_group_messages()
        
        # Log action
        app.logger.info(f"Admin {current_user.username} cleared chat history: {deleted_count} messages deleted")
        
        # Emit socket event để tất cả users refresh
        socketio.emit('chat_cleared', {}, broadcast=True)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count
        })
    except Exception as e:
        app.logger.error(f"Clear chat history error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Storage Layer (chat_storage.py)

### Function
```python
def clear_all_group_messages(self):
    """Xóa toàn bộ lịch sử chat tổng (receiver_id = 0)"""
    messages = self._load_messages()
    
    # Đếm số messages sẽ bị xóa
    deleted_count = 0
    messages_to_keep = []
    
    for msg in messages:
        if msg.get('receiver_id') == 0:
            # Xóa file đính kèm nếu có
            if msg.get('attachment_filename'):
                file_path = os.path.join(self.chat_uploads_dir, msg['attachment_filename'])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            deleted_count += 1
        else:
            # Giữ lại messages không phải group (1-1 chat cũ nếu có)
            messages_to_keep.append(msg)
    
    # Lưu lại messages
    self._save_messages(messages_to_keep)
    
    print(f"✓ Cleared {deleted_count} group chat messages")
    
    return deleted_count
```

## Flow hoạt động

### 1. Admin click "Xóa lịch sử chat"
```
User click nút "Xóa lịch sử chat"
  ↓
Hiển thị confirm dialog
  ↓
User confirm "OK"
  ↓
JavaScript gọi clearChatHistory()
  ↓
Fetch POST /chat/group/clear-history
```

### 2. Backend xử lý
```
Backend nhận request
  ↓
Kiểm tra current_user.role == 'admin'
  ↓
Nếu không phải admin → Return 403 Forbidden
  ↓
Nếu là admin:
  ↓
chat_storage.clear_all_group_messages()
  ↓
Xóa tất cả messages với receiver_id = 0
  ↓
Xóa tất cả file đính kèm
  ↓
Log action vào app.log
  ↓
Emit socket event 'chat_cleared' (broadcast)
  ↓
Return success + deleted_count
```

### 3. Frontend nhận response
```
Nhận response success
  ↓
Alert "✓ Đã xóa lịch sử chat!"
  ↓
Clear chatMessages innerHTML
  ↓
Reset lastMessageCount = 0
  ↓
Gọi loadMessages() (sẽ load empty)
```

### 4. Các users khác nhận socket event
```
Socket.IO emit 'chat_cleared' (broadcast)
  ↓
Tất cả clients connected nhận event
  ↓
Clear chatMessages innerHTML
  ↓
Reset lastMessageCount = 0
  ↓
Alert "⚠️ Lịch sử chat đã bị xóa bởi admin"
```

## Permission Control

### Chỉ admin mới có quyền xóa
```python
if current_user.role != 'admin':
    return jsonify({
        'success': False, 
        'error': 'Chỉ admin mới có quyền xóa lịch sử chat'
    }), 403
```

### User thường click nút
```
User thường click "Xóa lịch sử chat"
  ↓
Confirm dialog hiển thị
  ↓
User confirm "OK"
  ↓
Fetch POST /chat/group/clear-history
  ↓
Backend check role → Không phải admin
  ↓
Return 403 Forbidden
  ↓
Alert "✗ Lỗi: Chỉ admin mới có quyền xóa lịch sử chat"
```

## Những gì bị xóa

### ✅ Bị xóa
- Tất cả messages với `receiver_id = 0` (group messages)
- Tất cả file đính kèm của group messages
- Ảnh, video, documents trong chat tổng

### ❌ KHÔNG bị xóa
- Messages với `receiver_id != 0` (1-1 chat cũ nếu có)
- File đính kèm của 1-1 chat cũ
- User data, notes, documents khác

## Confirm Dialog

### Message
```
Xóa toàn bộ lịch sử chat?

Hành động này không thể hoàn tác!

Tất cả tin nhắn và file đính kèm sẽ bị xóa vĩnh viễn.
```

### Buttons
- **Cancel** - Hủy bỏ, không xóa
- **OK** - Xác nhận xóa

## Logs

### Console output
```
✓ Cleared 150 group chat messages
```

### App logs (data/logs/app.log)
```
[2025-11-15 09:46:55] INFO in app: Admin admin cleared chat history: 150 messages deleted
```

## Realtime Update

### Socket.IO broadcast
```javascript
// Backend emit
socketio.emit('chat_cleared', {}, broadcast=True)

// Frontend listen
socket.on('chat_cleared', () => {
  lastMessageCount = 0;
  document.getElementById('chatMessages').innerHTML = '';
  alert('⚠️ Lịch sử chat đã bị xóa bởi admin');
});
```

### Tất cả users online sẽ:
1. Thấy chat messages biến mất
2. Nhận alert notification
3. Chat area trống rỗng

## Testing

### Test 1: Admin xóa chat
```bash
1. Login với admin account
2. Truy cập /chat
3. Click dropdown menu (⋮)
4. Click "Xóa lịch sử chat"
5. Confirm dialog → Click OK
6. Kỳ vọng:
   - Alert "✓ Đã xóa lịch sử chat!"
   - Chat messages biến mất
   - Console log: "✓ Cleared X group chat messages"
```

### Test 2: User thường không có quyền
```bash
1. Login với user account (không phải admin)
2. Truy cập /chat
3. Click dropdown menu (⋮)
4. Click "Xóa lịch sử chat"
5. Confirm dialog → Click OK
6. Kỳ vọng:
   - Alert "✗ Lỗi: Chỉ admin mới có quyền xóa lịch sử chat"
   - Chat messages vẫn còn
```

### Test 3: Realtime update cho users khác
```bash
1. Mở 2 browsers:
   - Browser 1: Login admin
   - Browser 2: Login user thường
2. Browser 1: Click "Xóa lịch sử chat" → Confirm
3. Kỳ vọng Browser 2:
   - Chat messages biến mất
   - Alert "⚠️ Lịch sử chat đã bị xóa bởi admin"
```

### Test 4: File đính kèm bị xóa
```bash
1. Gửi message với file đính kèm
2. Check file tồn tại: data/uploads/chat/chat_XXX_...
3. Admin xóa lịch sử chat
4. Kỳ vọng:
   - File không còn tồn tại
   - Thư mục uploads/chat trống (hoặc chỉ có 1-1 chat files)
```

## Security

### 1. Permission check
```python
if current_user.role != 'admin':
    return jsonify({'success': False, 'error': '...'}, 403
```

### 2. Login required
```python
@login_required
def clear_group_chat_history():
```

### 3. Confirm dialog
```javascript
if(!confirm('Xóa toàn bộ lịch sử chat?...')){
    return;  // Cancel nếu user không confirm
}
```

### 4. Audit log
```python
app.logger.info(f"Admin {current_user.username} cleared chat history: {deleted_count} messages deleted")
```

## Rollback

Nếu muốn bỏ tính năng này:

### 1. Ẩn nút trong UI
```html
<!-- Comment out trong chat.html -->
<!--
<li><hr class="dropdown-divider"></li>
<li><a class="dropdown-item text-danger" href="#" onclick="clearChatHistory()">
  <i class="bi bi-trash"></i> Xóa lịch sử chat
</a></li>
-->
```

### 2. Disable route
```python
# Comment out trong app.py
# @app.route('/chat/group/clear-history', methods=['POST'])
# def clear_group_chat_history():
#     ...
```

## Best Practices

### 1. Backup trước khi xóa
```bash
# Backup chat_messages.json
cp data/chat_messages.json data/chat_messages_backup_$(date +%Y%m%d_%H%M%S).json

# Backup uploads
cp -r data/uploads/chat data/uploads/chat_backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Thông báo users trước
```
Gửi thông báo:
"Lịch sử chat sẽ bị xóa vào [thời gian]"
```

### 3. Chỉ xóa khi cần thiết
- Storage đầy
- Privacy compliance
- Dọn dẹp định kỳ

### 4. Review logs
```bash
# Xem ai đã xóa chat
cat data/logs/app.log | grep "cleared chat history"
```

## Lợi ích

### 1. **Quản lý storage**
- Xóa nhanh toàn bộ messages
- Giải phóng disk space
- Xóa cả file đính kèm

### 2. **Privacy**
- Xóa dữ liệu nhạy cảm
- Tuân thủ GDPR
- Reset chat room

### 3. **Maintenance**
- Dọn dẹp chat cũ
- Bắt đầu lại từ đầu
- Giữ chat room gọn gàng

### 4. **Control**
- Chỉ admin có quyền
- Có confirm dialog
- Có audit log
- Realtime notification

## Lưu ý

### ⚠️ Không thể hoàn tác
- Messages bị xóa vĩnh viễn
- File đính kèm bị xóa vĩnh viễn
- Không có recycle bin

### ⚠️ Ảnh hưởng tất cả users
- Tất cả users mất lịch sử chat
- Không thể xóa selective
- Broadcast notification cho tất cả

### ⚠️ Backup quan trọng
- Backup trước khi xóa
- Có thể restore nếu cần
- Giữ backup ít nhất 30 ngày

## Server status

**Server đang chạy**: http://127.0.0.1:5001

**Tính năng**: ✅ Active
**Permission**: Admin only
**Realtime**: Socket.IO broadcast

## Kết luận

✅ Đã thêm nút "Xóa lịch sử chat" vào dropdown
✅ Chỉ admin mới có quyền xóa
✅ Có confirm dialog để tránh xóa nhầm
✅ Xóa cả messages và file đính kèm
✅ Realtime notification cho tất cả users
✅ Có audit log để tracking
✅ Sẵn sàng sử dụng!
