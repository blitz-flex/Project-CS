export function initCounters() {
    document.querySelectorAll('.premium-card, .stat-item, .roadmap-step').forEach(el => {
        el.classList.add('visible');
        if (el.classList.contains('stat-item')) {
            startCounter(el);
        }
    });
}

function startCounter(el) {
    const h2 = el.querySelector('h2');
    if (!h2 || h2.dataset.counted) return;
    
    const target = parseInt(h2.innerText.replace(/\D/g,''));
    let count = 0;
    const duration = 1500;
    const increment = target / (duration / 16);
    
    const updateCount = () => {
        count += increment;
        if (count < target) {
            h2.innerText = Math.ceil(count) + (h2.innerText.includes('+') ? '+' : (h2.innerText.includes('%') ? '%' : ''));
            requestAnimationFrame(updateCount);
        } else {
            h2.innerText = target + (h2.innerText.includes('+') ? '+' : (h2.innerText.includes('%') ? '%' : ''));
        }
    };
    h2.dataset.counted = "true";
    updateCount();
}
