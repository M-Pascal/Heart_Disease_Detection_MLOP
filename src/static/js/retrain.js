document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.upload-form');
    const fileInput = document.getElementById('dataset-upload');
    const fileLabel = document.querySelector('.file-upload-label span');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const flashMessages = document.querySelector('.flash-messages');
    
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
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            loadingIndicator.style.display = 'flex';
            
            try {
                const formData = new FormData(form);
                const response = await fetch('/retrain', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    // The server will return the HTML with the flash message
                    const html = await response.text();
                    document.documentElement.innerHTML = html;
                } else {
                    throw new Error('Network response was not ok');
                }
            } catch (error) {
                console.error('Error:', error);
                loadingIndicator.style.display = 'none';
                
                // Create error message element
                const errorDiv = document.createElement('div');
                errorDiv.className = 'flash-error';
                errorDiv.innerHTML = '<i class="ri-error-warning-line"></i> An error occurred during retraining';
                flashMessages.appendChild(errorDiv);
            }
        });
    }
});