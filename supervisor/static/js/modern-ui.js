/* supervisor/static/js/modern-ui.js */
document.addEventListener('DOMContentLoaded', function() {
    
    // ── Animated Counter Logic ──
    const animateValue = (id, start, end, duration) => {
        if (start === end) return;
        let range = end - start;
        let current = start;
        let increment = end > start ? 1 : -1;
        let stepTime = Math.abs(Math.floor(duration / range));
        let obj = id;
        let timer = setInterval(function() {
            current += increment;
            obj.innerHTML = current;
            if (current == end) {
                clearInterval(timer);
            }
        }, stepTime);
    };

    const counters = document.querySelectorAll('.stat-value');
    counters.forEach(counter => {
        const target = parseInt(counter.innerText);
        if(!isNaN(target) && target > 0) {
            counter.innerText = '0';
            animateValue(counter, 0, target, 1500);
        }
    });

    // ── Toast Notification Bridge ──
    const messagesBridge = document.getElementById('django-messages-bridge');
    if (messagesBridge) {
        const messageElements = messagesBridge.querySelectorAll('.django-message-data');
        messageElements.forEach(el => {
            const level = el.dataset.level; // success, error, warning, info
            const text = el.innerText;
            
            // Map Django levels to SweetAlert icons
            let icon = 'success';
            if (level.includes('error') || level.includes('danger')) icon = 'error';
            if (level.includes('warning')) icon = 'warning';
            if (level.includes('info')) icon = 'info';

            Swal.fire({
                title: text,
                icon: icon,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 4000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                }
            });
        });
        messagesBridge.remove();
    }
});
