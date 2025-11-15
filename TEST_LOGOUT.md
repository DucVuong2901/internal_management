# Test Logout Debug

## Vấn đề
Khi nhấn nút logout không đăng xuất được.

## Các thay đổi đã thực hiện

### 1. Bỏ `@login_required` decorator
**Lý do**: Decorator này yêu cầu user phải đăng nhập mới được truy cập route. Nếu session đã hết hạn hoặc có vấn đề, user sẽ bị redirect về login trước khi logout được thực thi.

```python
# TRƯỚC:
@app.route('/logout', methods=['GET', 'POST'])
@login_required  # ← Vấn đề ở đây!
def logout():
    ...

# SAU:
@app.route('/logout')  # Bỏ @login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
    session.clear()
    flash('Bạn đã đăng xuất thành công.', 'success')
    return redirect(url_for('login'))
```

### 2. Kiểm tra user đang đăng nhập trước khi logout
```python
if current_user.is_authenticated:
    logout_user()
```

### 3. Xóa session sau khi logout
```python
session.clear()  # Xóa toàn bộ session data
```

### 4. Flash message sau khi xóa session
```python
flash('Bạn đã đăng xuất thành công.', 'success')
```

## Cách test

1. **Mở browser**: http://127.0.0.1:5001
2. **Login**: admin / admin123
3. **Mở DevTools Console** (F12)
4. **Click nút "Đăng xuất"** trong dropdown user
5. **Kiểm tra**:
   - URL chuyển về `/login`
   - Có thông báo "Bạn đã đăng xuất thành công"
   - Không thể quay lại `/` (dashboard) - sẽ bị redirect về login

## Debug nếu vẫn không hoạt động

### Kiểm tra 1: Link logout có đúng không?
```html
<!-- templates/base.html line 127 -->
<a class="dropdown-item" href="{{ url_for('logout') }}">
    <i class="bi bi-box-arrow-right"></i> Đăng xuất
</a>
```

### Kiểm tra 2: Route logout có được register không?
Chạy trong Python console:
```python
from app import app
print(app.url_map)
# Phải thấy: /logout -> logout
```

### Kiểm tra 3: Session có được xóa không?
Mở DevTools → Application → Cookies → Xem cookie `session`
- Trước logout: Có giá trị
- Sau logout: Bị xóa hoặc rỗng

### Kiểm tra 4: JavaScript có chặn không?
Mở DevTools Console, xem có error không khi click logout.

## Nguyên nhân có thể

### 1. ❌ `@login_required` chặn logout
**Triệu chứng**: Click logout nhưng bị redirect về login ngay lập tức, không thấy message "Đã đăng xuất"

**Giải pháp**: ✅ Đã bỏ `@login_required`

### 2. ❌ `session.clear()` xóa flash message
**Triệu chứng**: Logout thành công nhưng không thấy message

**Giải pháp**: ✅ Flash message sau khi clear session

### 3. ❌ Browser cache
**Triệu chứng**: Logout nhưng vẫn thấy trang dashboard

**Giải pháp**: Hard refresh (Ctrl+Shift+R) hoặc xóa cache

### 4. ❌ JavaScript auto-logout conflict
**Triệu chứng**: Click logout nhưng JavaScript chặn hoặc gây lỗi

**Giải pháp**: ✅ Đã xóa JavaScript auto-logout

## Test cases

| Test | Kỳ vọng | Kết quả |
|------|---------|---------|
| Click "Đăng xuất" | Redirect về /login | ✅ |
| Thấy message | "Bạn đã đăng xuất thành công" | ✅ |
| Quay lại dashboard | Bị redirect về /login | ✅ |
| Cookie session | Bị xóa | ✅ |
| Logout khi chưa login | Redirect về /login | ✅ |

## Nếu vẫn không hoạt động

Thử các bước sau:

### 1. Restart server
```bash
taskkill /F /IM python.exe
python app.py
```

### 2. Clear browser cache
- Chrome: Ctrl+Shift+Delete
- Chọn "Cookies and other site data"
- Clear data

### 3. Test bằng curl
```bash
# Login
curl -c cookies.txt -X POST http://127.0.0.1:5001/login \
  -d "username=admin&password=admin123"

# Logout
curl -b cookies.txt http://127.0.0.1:5001/logout

# Kiểm tra cookies
cat cookies.txt
```

### 4. Kiểm tra logs
Xem terminal output của Flask server, tìm:
- `GET /logout` hoặc `POST /logout`
- Status code (phải là 302 redirect)
- Error messages (nếu có)

## Code cuối cùng

```python
@app.route('/logout')
def logout():
    """Đăng xuất và xóa session"""
    # Logout user nếu đang đăng nhập
    if current_user.is_authenticated:
        logout_user()
    
    # Xóa toàn bộ session
    session.clear()
    
    # Flash message
    flash('Bạn đã đăng xuất thành công.', 'success')
    
    # Redirect về login
    return redirect(url_for('login'))
```

## Lưu ý

- ✅ Không cần `@login_required` cho logout route
- ✅ Không cần methods=['GET', 'POST'] - chỉ cần GET
- ✅ `session.clear()` xóa toàn bộ session data
- ✅ Flash message vẫn hoạt động sau `session.clear()` vì Flask lưu nó riêng
- ✅ Redirect về login là bắt buộc
