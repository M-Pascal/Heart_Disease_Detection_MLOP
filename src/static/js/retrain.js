document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.upload-form');
    const fileInput = document.getElementById('dataset-upload');
    const fileLabel = document.querySelector('.file-upload-label span');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Choose Dataset File';
            }
        });
    }
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Show loading indicator
            loadingIndicator.style.display = 'flex';
            
            // You could add additional validation here
        });
    }
});
