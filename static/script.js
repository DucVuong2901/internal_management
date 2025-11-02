// Dark Mode Toggle
function initDarkMode() {
    const darkModeToggleDropdown = document.getElementById('darkModeToggleDropdown');
    const darkModeIconDropdown = document.getElementById('darkModeIconDropdown');
    const darkModeTextDropdown = document.getElementById('darkModeTextDropdown');
    const html = document.documentElement;
    
    // Helper function to update all icons and text
    function updateThemeUI(isDark) {
        if (darkModeIconDropdown) {
            darkModeIconDropdown.className = isDark ? 'bi bi-sun' : 'bi bi-moon-stars';
        }
        if (darkModeTextDropdown) {
            darkModeTextDropdown.textContent = isDark ? 'Chế độ sáng' : 'Chế độ tối';
        }
    }
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        updateThemeUI(true);
        try { reapplyNoteCardColors(); } catch(_) {}
    } else {
        updateThemeUI(false);
    }
    
    // Toggle theme function
    function toggleTheme() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeUI(newTheme === 'dark');
        
        // Áp dụng lại màu chữ tương phản cho ghi chú
        try { reapplyNoteCardColors(); } catch(_) {}
    }
    
    // Attach event listener to dropdown toggle
    if (darkModeToggleDropdown) {
        darkModeToggleDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            toggleTheme();
            // Close the dropdown after toggling
            const dropdown = bootstrap.Dropdown.getInstance(document.getElementById('userDropdown'));
            if (dropdown) {
                dropdown.hide();
            }
        });
    }
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
    
    // Tự động logout khi đóng tab/window
    if (document.body.hasAttribute('data-authenticated')) {
        let isUnloading = false;
        
        // Sử dụng beforeunload để logout khi đóng tab
        window.addEventListener('beforeunload', function(e) {
            if (!isUnloading) {
                isUnloading = true;
                // Sử dụng navigator.sendBeacon để gửi logout request (đáng tin cậy hơn fetch)
                try {
                    navigator.sendBeacon('/api/logout');
                } catch(err) {
                    // Fallback: sử dụng fetch với keepalive
                    fetch('/api/logout', {
                        method: 'POST',
                        keepalive: true,
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }).catch(() => {}); // Ignore errors khi đóng tab
                }
            }
        });
        
        // Phát hiện khi pagehide (khi tab đóng)
        window.addEventListener('pagehide', function(e) {
            if (e.persisted === false) {
                // Tab không được cache = có thể đã đóng
                try {
                    navigator.sendBeacon('/api/logout');
                } catch(err) {
                    fetch('/api/logout', {
                        method: 'POST',
                        keepalive: true
                    }).catch(() => {});
                }
            }
        });
    }
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

