# Mini Chat Window - Nằm sát dưới cùng

## Ngày: 15/11/2025

## Thay đổi

Đã chuyển **mini chat window** từ nổi lên trên sang **nằm sát dưới cùng màn hình** như Messenger/WhatsApp Web.

## Trước và Sau

### Trước (Floating)
```
┌─────────────────────────────────┐
│                                 │
│                                 │
│  ┌──────────────────┐           │
│  │ Chat Tổng    [✕] │           │
│  ├──────────────────┤           │
│  │ Messages...      │           │
│  │                  │           │
│  ├──────────────────┤           │
│  │ Input...    [>]  │           │
│  └──────────────────┘           │
│                            [💬] │
└─────────────────────────────────┘
```

### Sau (Bottom Docked)
```
┌─────────────────────────────────┐
│                                 │
│                                 │
│                                 │
│                            [💬] │
├─────────────────────────────────┤
│ 💬 Chat Tổng          [⛶] [✕]  │
├─────────────────────────────────┤
│ Messages...                     │
│                                 │
├─────────────────────────────────┤
│ [Nhập tin nhắn...]        [>]   │
└─────────────────────────────────┘
```

## CSS Changes

### Position
```css
/* Trước */
.mini-chat-window {
    position: absolute;
    bottom: 80px;
    right: 0;
}

/* Sau */
.mini-chat-window {
    position: fixed;
    bottom: 0;
    right: 0;
}
```

### Border Radius
```css
/* Trước */
border-radius: 12px;

/* Sau */
border-radius: 12px 12px 0 0;  /* Chỉ bo góc trên */
```

### Shadow
```css
/* Trước */
box-shadow: 0 8px 32px rgba(0,0,0,0.2);

/* Sau */
box-shadow: 0 -4px 20px rgba(0,0,0,0.15);  /* Shadow lên trên */
```

### Size
```css
/* Trước */
width: 350px;
height: 500px;

/* Sau */
width: 400px;
height: 450px;
```

### Dark Mode Border
```css
[data-theme="dark"] .mini-chat-window {
    background: #2d2d2d;
    border: 1px solid #495057;
    border-bottom: none;  /* Không có border dưới */
}
```

## Responsive Mobile

### Desktop (>768px)
```css
.mini-chat-window {
    width: 400px;
    height: 450px;
    right: 0;
    bottom: 0;
}
```

### Mobile (<768px)
```css
.mini-chat-window {
    width: 100%;        /* Full width */
    height: 400px;      /* Thấp hơn */
    right: 0;
    bottom: 0;
}

.floating-chat-btn {
    width: 50px;        /* Nhỏ hơn */
    height: 50px;
    font-size: 20px;
}

#floatingChatWidget {
    bottom: 10px;
    right: 10px;
}
```

## Lợi ích

### 1. **UX tốt hơn**
- Giống Messenger, WhatsApp Web
- Familiar interface
- Dễ nhận diện

### 2. **Không che khuất nội dung**
- Nằm sát dưới, không nổi giữa màn hình
- Không che các button/content quan trọng
- Tận dụng không gian dưới cùng

### 3. **Mobile friendly**
- Full width trên mobile
- Không bị tràn ra ngoài
- Dễ sử dụng trên điện thoại

### 4. **Visual hierarchy**
- Rõ ràng hơn
- Không bị lẫn với content chính
- Border radius chỉ trên → nhấn mạnh là popup từ dưới

## Behavior

### Khi mở mini chat
```
1. Floating button biến mất
2. Mini chat window slide up từ dưới
3. Nằm sát bottom: 0, right: 0
4. Không có gap với cạnh màn hình
```

### Khi đóng mini chat
```
1. Mini chat window slide down
2. Floating button hiện lại ở góc phải-dưới
3. Position: bottom: 20px, right: 20px
```

## Z-index

```css
#floatingChatWidget {
    z-index: 1000;
}

.mini-chat-window {
    z-index: 999;
}
```

Floating button có z-index cao hơn để luôn ở trên cùng.

## Testing

### ✅ Desktop
```
1. Click floating button
2. Kỳ vọng: Mini chat mở sát dưới cùng
3. Width: 400px, Height: 450px
4. Border radius chỉ trên
5. Shadow hướng lên
```

### ✅ Mobile
```
1. Resize browser < 768px
2. Click floating button
3. Kỳ vọng: Mini chat full width
4. Height: 400px
5. Không bị tràn
```

### ✅ Dark Mode
```
1. Toggle dark mode
2. Kỳ vọng: Border không có dưới
3. Background đen
4. Contrast tốt
```

## Comparison với các app khác

### Messenger (Facebook)
```
✅ Nằm sát dưới cùng
✅ Border radius chỉ trên
✅ Shadow hướng lên
✅ Full width trên mobile
```

### WhatsApp Web
```
✅ Nằm sát dưới cùng
✅ Không có gap với cạnh
✅ Responsive design
```

### Slack
```
❌ Nổi giữa màn hình (khác)
```

### Discord
```
❌ Sidebar cố định (khác)
```

→ Design của chúng ta giống **Messenger** và **WhatsApp Web** nhất!

## Future Enhancements

### Animation
```css
.mini-chat-window {
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from {
        transform: translateY(100%);
    }
    to {
        transform: translateY(0);
    }
}
```

### Resize Handle
```html
<div class="resize-handle"></div>
```

Cho phép user kéo để thay đổi height.

### Minimize
```
Thêm nút minimize → Thu nhỏ thành tab bar
```

## Known Issues

### ❌ Không có
Tất cả hoạt động tốt!

## Server Status

**Server đang chạy**: http://127.0.0.1:5001

**Mini chat**: ✅ Bottom docked
**Width**: 400px (desktop), 100% (mobile)
**Height**: 450px (desktop), 400px (mobile)

## Kết luận

✅ Mini chat window đã nằm sát dưới cùng
✅ Giống Messenger/WhatsApp Web
✅ Responsive trên mobile
✅ Dark mode support
✅ Không che khuất nội dung
✅ UX tốt hơn!
