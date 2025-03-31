document.addEventListener('DOMContentLoaded', function() {
    // Counter animation
    const counter = document.getElementById('clientCounter');
    if (counter) {
        let count = 0;
        const target = parseInt(counter.textContent);
        const increment = target / 50;
        
        const updateCounter = () => {
            count += increment;
            if (count < target) {
                counter.textContent = Math.floor(count) + '+';
                setTimeout(updateCounter, 20);
            } else {
                counter.textContent = target + '+';
            }
        };
        
        updateCounter();
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
