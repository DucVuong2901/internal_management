// Dark Mode Toggle
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    const html = document.documentElement;
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        if (darkModeIcon) {
            darkModeIcon.className = 'bi bi-sun';
        }
        try { reapplyNoteCardColors(); } catch(_) {}
    }
    
    // Toggle theme
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            if (darkModeIcon) {
                darkModeIcon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
            }
            // Áp dụng lại màu chữ tương phản cho ghi chú
            try { reapplyNoteCardColors(); } catch(_) {}
        });
    }
}

// Toggle draggable + persist position
function initDraggableToggle() {
    const btn = document.getElementById('darkModeToggle');
    if (!btn) return;

    // Restore position and decide lock state
    const saved = localStorage.getItem('darkTogglePos');
    const savedLock = localStorage.getItem('darkToggleLocked');
    let hasSavedPos = false;
    if (saved) {
        try {
            const pos = JSON.parse(saved);
            if (typeof pos.left === 'number' && typeof pos.top === 'number') {
                btn.style.left = pos.left + 'px';
                btn.style.top = pos.top + 'px';
                btn.style.right = 'auto';
                btn.style.bottom = 'auto';
                hasSavedPos = true;
            }
        } catch(_) {}
    }

    // If already locked (or has saved pos), keep it fixed and do not add drag handlers
    if (savedLock === 'true' || hasSavedPos) {
        // ensure lock flag is set so future loads keep it fixed
        localStorage.setItem('darkToggleLocked', 'true');
        return;
    }

    // Otherwise allow one-time drag then lock on drop
    let isDragging = false;
    let offsetX = 0, offsetY = 0;

    function onPointerDown(e){
        isDragging = true;
        const rect = btn.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        offsetX = clientX - rect.left;
        offsetY = clientY - rect.top;
        const currentRect = btn.getBoundingClientRect();
        btn.style.left = currentRect.left + 'px';
        btn.style.top = currentRect.top + 'px';
        btn.style.right = 'auto';
        btn.style.bottom = 'auto';
        document.addEventListener('mousemove', onPointerMove);
        document.addEventListener('mouseup', onPointerUp);
        document.addEventListener('touchmove', onPointerMove, {passive:false});
        document.addEventListener('touchend', onPointerUp);
        if (e.cancelable) e.preventDefault();
        e.stopPropagation();
    }

    function onPointerMove(e){
        if (!isDragging) return;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        let x = clientX - offsetX;
        let y = clientY - offsetY;
        const m = 6;
        x = Math.min(vw - btn.offsetWidth - m, Math.max(m, x));
        y = Math.min(vh - btn.offsetHeight - m, Math.max(m, y));
        btn.style.left = x + 'px';
        btn.style.top = y + 'px';
        if (e.cancelable) e.preventDefault();
    }

    function onPointerUp(){
        if (!isDragging) return;
        isDragging = false;
        document.removeEventListener('mousemove', onPointerMove);
        document.removeEventListener('mouseup', onPointerUp);
        document.removeEventListener('touchmove', onPointerMove);
        document.removeEventListener('touchend', onPointerUp);
        const left = parseInt(btn.style.left || '0', 10);
        const top = parseInt(btn.style.top || '0', 10);
        localStorage.setItem('darkTogglePos', JSON.stringify({left, top}));
        localStorage.setItem('darkToggleLocked', 'true');
    }

    btn.addEventListener('mousedown', onPointerDown);
    btn.addEventListener('touchstart', onPointerDown, {passive:false});
}

// KHÔNG check session để tránh logout khi chuyển tab
// Session cookie (session-only) sẽ tự động logout khi đóng trình duyệt
function checkSessionOnLoad() {
    // Disabled - không check session để tránh logout khi chuyển tab/navigate
    // Session cookie (không có expires) sẽ tự động xóa khi đóng trình duyệt
    return;
}

// Global Search Auto-complete
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initDarkMode();
    initDraggableToggle();
    try { reapplyNoteCardColors(); } catch(_) {}
    
    // Kiểm tra session khi load trang
    checkSessionOnLoad();
    
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        let searchTimeout;
        
        globalSearch.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length > 2) {
                searchTimeout = setTimeout(() => {
                    fetch(`/api/search?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            // You can implement a dropdown here if needed
                            console.log('Search results:', data);
                        })
                        .catch(error => console.error('Search error:', error));
                }, 300);
            }
        });
    }
    
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Bạn có chắc muốn xóa mục này?')) {
                e.preventDefault();
            }
        });
    });
    
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // KHÔNG xóa sessionStorage khi unload để tránh logout khi chuyển tab
    // Session cookie (session-only) sẽ tự động xóa khi đóng trình duyệt
});

// Note và Doc content được xem trong tab mới, không cần toggle functions nữa

// Helpers cho đối lập màu chữ theo nền
function _hexToRgb(hex){
    if (!hex) return {r:255,g:255,b:255};
    hex = hex.replace('#','');
    if (hex.length === 3) hex = hex.split('').map(c=>c+c).join('');
    const num = parseInt(hex,16);
    return { r:(num>>16)&255, g:(num>>8)&255, b:num&255 };
}
function _getLuminance(hex){
    const c = _hexToRgb(hex);
    const srgb = v=>{ v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
    const r=srgb(c.r), g=srgb(c.g), b=srgb(c.b);
    return 0.2126*r + 0.7152*g + 0.0722*b;
}
function _pickTextColorForBg(bgHex){
    // Yêu cầu mới: chữ luôn màu đen khi có nền tùy chỉnh
    return '#212529';
}
function reapplyNoteCardColors(){
    const cards = document.querySelectorAll('.clickable-card[data-note-id]');
    cards.forEach(card=>{
        const id = card.getAttribute('data-note-id');
        const saved = localStorage.getItem('noteColor:'+id);
        if (saved) {
            // set bg cho card + header/body
            card.style.backgroundColor = saved;
            const header = card.querySelector('.card-header');
            const body = card.querySelector('.card-body');
            if (header) header.style.backgroundColor = saved;
            if (body) body.style.backgroundColor = saved;
            // text color → luôn đen
            const color = _pickTextColorForBg(saved);
            if (color) card.style.color = color;
            card.classList.add('custom-colored-note');
        }
    });
}

// Format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return date.toLocaleDateString('vi-VN', options);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

