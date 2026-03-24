document.addEventListener("DOMContentLoaded", () => {
    // Basic Fade In
    gsap.fromTo(".gs-fade-in", 
        { opacity: 0 }, 
        { opacity: 1, duration: 0.8, ease: "power2.out" }
    );

    // Fade Up specific elements
    gsap.fromTo(".gs-reveal-up",
        { opacity: 0, y: 30 },
        { 
            opacity: 1, 
            y: 0, 
            duration: 0.8, 
            stagger: 0.1, 
            ease: "power3.out" 
        }
    );

    // Number counters for stats
    document.querySelectorAll(".gs-counter").forEach(el => {
        const text = el.innerText;
        const isPercent = text.includes('%');
        const targetValue = parseFloat(text.replace('%', ''));
        
        if(isNaN(targetValue)) return;

        gsap.fromTo(el, 
            { innerHTML: 0 }, 
            { 
                innerHTML: targetValue, 
                duration: 2, 
                ease: "power2.out",
                snap: { innerHTML: 1 },
                onUpdate: () => {
                    el.innerHTML = Math.round(el.innerHTML) + (isPercent ? '%' : '');
                }
            }
        );
    });

    // Mobile Nav Toggle
    const navBtn = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (navBtn && navLinks) {
        navBtn.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
    }
});
