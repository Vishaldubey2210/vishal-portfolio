// ==================== PARTICLES BACKGROUND ====================
const particlesCanvas = document.getElementById('particles-canvas');
const ctx = particlesCanvas.getContext('2d');

particlesCanvas.width = window.innerWidth;
particlesCanvas.height = window.innerHeight;

const particles = [];
const particleCount = 100;

class Particle {
    constructor() {
        this.x = Math.random() * particlesCanvas.width;
        this.y = Math.random() * particlesCanvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > particlesCanvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > particlesCanvas.height) this.vy *= -1;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#00F5FF';
        ctx.fill();
    }
}

// Create particles
for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
}

// Animation loop
function animateParticles() {
    ctx.clearRect(0, 0, particlesCanvas.width, particlesCanvas.height);

    particles.forEach((particle, i) => {
        particle.update();
        particle.draw();

        // Draw connections
        particles.slice(i + 1).forEach(otherParticle => {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                ctx.beginPath();
                ctx.moveTo(particle.x, particle.y);
                ctx.lineTo(otherParticle.x, otherParticle.y);
                ctx.strokeStyle = `rgba(0, 245, 255, ${1 - distance / 100})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        });
    });

    requestAnimationFrame(animateParticles);
}

animateParticles();

// Resize handler
window.addEventListener('resize', () => {
    particlesCanvas.width = window.innerWidth;
    particlesCanvas.height = window.innerHeight;
});

// ==================== CURSOR TRAIL ====================
const cursorCanvas = document.getElementById('cursor-trail');
const cursorCtx = cursorCanvas.getContext('2d');

cursorCanvas.width = window.innerWidth;
cursorCanvas.height = window.innerHeight;

const trail = [];
const maxTrailLength = 20;

document.addEventListener('mousemove', (e) => {
    trail.push({ x: e.clientX, y: e.clientY, life: 1 });

    if (trail.length > maxTrailLength) {
        trail.shift();
    }
});

function animateCursorTrail() {
    cursorCtx.clearRect(0, 0, cursorCanvas.width, cursorCanvas.height);

    trail.forEach((point, index) => {
        point.life -= 0.05;

        if (point.life > 0) {
            cursorCtx.beginPath();
            cursorCtx.arc(point.x, point.y, 3, 0, Math.PI * 2);
            cursorCtx.fillStyle = `rgba(0, 245, 255, ${point.life})`;
            cursorCtx.fill();
        }
    });

    // Remove dead points
    while (trail.length > 0 && trail[0].life <= 0) {
        trail.shift();
    }

    requestAnimationFrame(animateCursorTrail);
}

animateCursorTrail();

window.addEventListener('resize', () => {
    cursorCanvas.width = window.innerWidth;
    cursorCanvas.height = window.innerHeight;
});
