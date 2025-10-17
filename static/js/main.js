// ==================== SOCKET.IO CONNECTION ====================
const socket = io();

// ==================== VISITOR COUNTER ====================
socket.on('visitor_count', (data) => {
    const counterElement = document.getElementById('visitor-count');
    if (counterElement) {
        counterElement.textContent = data.count;
    }
});

// ==================== NAVBAR SCROLL EFFECT ====================
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ==================== THEME TOGGLE ====================
const themeToggle = document.getElementById('theme-toggle');
let isDark = true;

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        document.documentElement.classList.toggle('light');
        const icon = themeToggle.querySelector('i');
        icon.className = isDark ? 'fas fa-moon' : 'fas fa-sun';
        playSound('click');
    });
}

// ==================== SOUND TOGGLE ====================
const soundToggle = document.getElementById('sound-toggle');
let soundEnabled = true;

if (soundToggle) {
    soundToggle.addEventListener('click', () => {
        soundEnabled = !soundEnabled;
        const icon = soundToggle.querySelector('i');
        icon.className = soundEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
        localStorage.setItem('soundEnabled', soundEnabled);
    });
}

// Load sound preference
if (localStorage.getItem('soundEnabled') === 'false') {
    soundEnabled = false;
    if (soundToggle) {
        soundToggle.querySelector('i').className = 'fas fa-volume-mute';
    }
}

// ==================== SOUND EFFECTS ====================
function playSound(type) {
    if (!soundEnabled) return;
    
    const sounds = {
        click: '/static/sounds/click.mp3',
        hover: '/static/sounds/hover.mp3'
    };
    
    if (sounds[type]) {
        const audio = new Audio(sounds[type]);
        audio.volume = 0.3;
        audio.play().catch(e => console.log('Audio play failed'));
    }
}

// Add hover sounds to links
document.querySelectorAll('a, button').forEach(element => {
    element.addEventListener('mouseenter', () => playSound('hover'));
    element.addEventListener('click', () => playSound('click'));
});

// ==================== ANALYTICS TRACKING ====================
// Track page views
socket.emit('page_view', {
    page: window.location.pathname,
    timestamp: new Date()
});

// Track clicks
document.addEventListener('click', (e) => {
    socket.emit('click_event', {
        x: e.clientX,
        y: e.clientY,
        element: e.target.tagName,
        timestamp: new Date()
    });
});

// ==================== SMOOTH SCROLL ====================
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

// ==================== SCROLL ANIMATIONS ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-slide-up');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('[data-aos]').forEach(el => {
    observer.observe(el);
});

// ==================== CONSOLE MESSAGE ====================
console.log('%c🚀 Vishal Kumar Portfolio', 'font-size: 20px; color: #00F5FF; font-weight: bold;');
console.log('%cBuilt with Flask, Bootstrap & Socket.IO', 'font-size: 12px; color: #BD00FF;');
console.log('%cLooking for developers? Hire me!', 'font-size: 14px; color: #39FF14;');
