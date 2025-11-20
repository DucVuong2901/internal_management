# ✅ Mini Chat: Gửi Hình Ảnh & File

## 🎯 Tính Năng Mới

Mini chat widget (floating chat) giờ đây hỗ trợ **gửi hình ảnh và file đính kèm**!

## ✨ Chức Năng

### 1. **Nút Đính Kèm**
- ✅ Icon 📎 (paperclip) trong textarea
- ✅ Click để chọn file
- ✅ Hỗ trợ mọi loại file

### 2. **File Preview**
- ✅ Hiển thị tên file sau khi chọn
- ✅ Nút "Xóa" để hủy file
- ✅ Gửi kèm message hoặc chỉ file

### 3. **Hiển Thị Trong Chat**
- ✅ **Hình ảnh**: Preview thumbnail 150px
- ✅ **File khác**: Link download với icon
- ✅ Click hình để xem full size

## 🔧 Thay Đổi Kỹ Thuật

### HTML Structure
```html
<form id="miniChatForm" enctype="multipart/form-data">
  <div class="position-relative">
    <!-- Textarea -->
    <textarea id="miniMessageInput"></textarea>
    
    <!-- Paperclip button -->
    <button onclick="miniFileInput.click()">
      <i class="bi bi-paperclip"></i>
    </button>
    
    <!-- Hidden file input -->
    <input type="file" id="miniFileInput" name="attachment">
  </div>
  
  <!-- Send button -->
  <button type="submit">Send</button>
</form>

<!-- File preview -->
<div id="miniFilePreview" style="display:none;">
  <span id="miniFileName"></span>
  <button onclick="clearMiniFile()">Xóa</button>
</div>
```

### JavaScript Functions

#### 1. Form Submit
```javascript
document.getElementById('miniChatForm').addEventListener('submit', async e => {
  e.preventDefault();
  const msg = input.value.trim();
  const fileInput = document.getElementById('miniFileInput');
  
  // Phải có message hoặc file
  if (!msg && !fileInput.files.length) return;
  
  const fd = new FormData();
  if (msg) fd.append('message', msg);
  if (fileInput.files.length) fd.append('attachment', fileInput.files[0]);
  
  // Send to server
  const r = await fetch('/chat/group/send', {method: 'POST', body: fd});
  
  if (success) {
    clearMiniFile();
    loadMiniChatMessages();
  }
});
```

#### 2. File Preview
```javascript
function showMiniFilePreview(file) {
  const preview = document.getElementById('miniFilePreview');
  const fileName = document.getElementById('miniFileName');
  fileName.textContent = file.name;
  preview.style.display = 'block';
}

function clearMiniFile() {
  const fileInput = document.getElementById('miniFileInput');
  const preview = document.getElementById('miniFilePreview');
  if (fileInput) fileInput.value = '';
  if (preview) preview.style.display = 'none';
}
```

#### 3. Display Messages
```javascript
function displayMiniMessages(msgs) {
  msgs.forEach(m => {
    let bubbleContent = '';
    
    // Message text
    if (m.message) {
      bubbleContent += escapeHtml(m.message);
    }
    
    // Attachment
    if (m.attachment_filename) {
      const isImg = /\.(jpg|jpeg|png|gif|webp|bmp)$/.test(ext);
      
      if (isImg) {
        // Image preview
        bubbleContent += `<img src="/chat/download/${filename}" 
                              style="max-width:150px;" 
                              onclick="window.open(...)">`;
      } else {
        // File download link
        bubbleContent += `<a href="/chat/download/${filename}" download>
                            <i class="bi bi-file-earmark"></i> ${name}
                          </a>`;
      }
    }
  });
}
```

## 🎨 UI/UX

### Gửi File:
```
┌─────────────────────────────┐
│ Mini Chat                   │
├─────────────────────────────┤
│ Messages...                 │
├─────────────────────────────┤
│ ┌─────────────────────┐     │
│ │ Nhập tin nhắn... 📎 │ [>] │
│ └─────────────────────┘     │
│ 📎 image.png [Xóa]          │
└─────────────────────────────┘
```

### Hiển Thị:
```
┌─────────────────────────────┐
│ User A                      │
│ ┌─────────────────────┐     │
│ │ Check hình này nhé  │     │
│ │ [Image Preview]     │     │
│ └─────────────────────┘     │
│                             │
│ User B                      │
│ ┌─────────────────────┐     │
│ │ 📄 document.pdf     │     │
│ └─────────────────────┘     │
└─────────────────────────────┘
```

## 📱 Responsive

### Desktop:
- Image preview: 150px max-width
- File link: Full filename

### Mobile:
- Image preview: 120px max-width
- File link: Truncated if too long

## 🎯 Workflow

### Gửi Hình Ảnh:
```
1. Click icon 📎
2. Chọn hình từ máy
3. Preview tên file hiện ra
4. (Optional) Nhập message
5. Click Send
6. Hình gửi đi và hiển thị thumbnail
```

### Gửi File:
```
1. Click icon 📎
2. Chọn file (PDF, DOC, etc.)
3. Preview tên file
4. (Optional) Nhập message
5. Click Send
6. File gửi đi với link download
```

### Xem Hình/File:
```
Hình ảnh:
- Click thumbnail → Mở full size tab mới

File:
- Click link → Download file
```

## ✨ Tính Năng Đặc Biệt

### 1. **Paste Image**
- Paste từ clipboard vẫn hoạt động
- Tự động attach vào form

### 2. **Drag & Drop**
- Kéo thả file vào chat area
- Tự động attach

### 3. **Multiple Formats**
- ✅ Images: JPG, PNG, GIF, WebP, BMP
- ✅ Documents: PDF, DOC, DOCX, XLS, XLSX
- ✅ Archives: ZIP, RAR
- ✅ Others: TXT, CSV, etc.

### 4. **File Size Limit**
- Theo storage limit của user
- Hiển thị error nếu quá giới hạn

## 🧪 Test Cases

### Test 1: Gửi Hình
```
1. Mở mini chat
2. Click 📎
3. Chọn image.jpg
4. Thấy "📎 image.jpg [Xóa]"
5. Click Send
6. Hình hiển thị trong chat
7. Click hình → Mở full size
```

### Test 2: Gửi File
```
1. Click 📎
2. Chọn document.pdf
3. Thấy "📎 document.pdf [Xóa]"
4. Click Send
5. File hiển thị với icon 📄
6. Click link → Download file
```

### Test 3: Gửi Kèm Message
```
1. Nhập "Check file này"
2. Click 📎, chọn file
3. Click Send
4. Hiển thị message + file
```

### Test 4: Xóa File
```
1. Chọn file
2. Click [Xóa]
3. File preview biến mất
4. Input file reset
```

### Test 5: Chỉ Gửi File
```
1. Không nhập message
2. Chỉ chọn file
3. Click Send
4. File gửi thành công
```

## 🎉 Kết Quả

### Trước:
- ❌ Mini chat chỉ gửi text
- ❌ Phải vào full chat để gửi file
- ❌ Không tiện lợi

### Bây Giờ:
- ✅ **Gửi hình ảnh** ngay trong mini chat
- ✅ **Gửi file** mọi loại
- ✅ **Preview thumbnail** cho hình
- ✅ **Download link** cho file
- ✅ **Tiện lợi** như full chat

## 💡 Use Cases

### 1. Quick Screenshot Share
```
User: "Lỗi này fix thế nào?"
→ Paste screenshot
→ Send
→ Team thấy ngay
```

### 2. Document Share
```
User: "Tài liệu họp"
→ Attach PDF
→ Send
→ Everyone download
```

### 3. Image Discussion
```
User: "Design mới"
→ Send image
→ Click to view full
→ Discuss
```

## 🔒 Security

- ✅ File type validation
- ✅ Size limit check
- ✅ Secure filename handling
- ✅ Storage quota enforcement

## 📊 Comparison

| Feature | Full Chat | Mini Chat (Cũ) | Mini Chat (Mới) |
|---------|-----------|----------------|-----------------|
| Send text | ✅ | ✅ | ✅ |
| Send image | ✅ | ❌ | **✅** |
| Send file | ✅ | ❌ | **✅** |
| Image preview | ✅ | ❌ | **✅** |
| File download | ✅ | ❌ | **✅** |
| Paste image | ✅ | ❌ | **✅** |
| Drag & drop | ✅ | ❌ | **✅** |

Mini chat giờ đây **tương đương** full chat về tính năng! 🎉
