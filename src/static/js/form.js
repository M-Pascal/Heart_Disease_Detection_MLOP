document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Show loading indicator
            loadingIndicator.style.display = 'flex';
            
            // You could add form validation here if needed
            // If validation fails, prevent form submission
            // e.preventDefault();
        });
    }
    
    // Add input validation if needed
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            const min = parseInt(this.min);
            const max = parseInt(this.max);
            const value = parseInt(this.value);
            
            if (value < min) this.value = min;
            if (value > max) this.value = max;
        });
    });
});
