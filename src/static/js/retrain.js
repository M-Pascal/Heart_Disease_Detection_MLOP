document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.upload-form');
    const fileInput = document.getElementById('dataset-upload');
    const fileLabel = document.querySelector('.file-upload-label span');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const retrainStatus = document.getElementById('retrainStatus');
    
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
            retrainStatus.style.display = 'none';
            
            try {
                const formData = new FormData(form);
                const response = await fetch('/retrain', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    retrainStatus.innerHTML = `
                        <i class="ri-checkbox-circle-line"></i>
                        ${result.message}
                        <span class="accuracy-display">Accuracy: ${result.accuracy}</span>
                    `;
                    retrainStatus.className = 'retrain-status success';
                } else {
                    retrainStatus.innerHTML = `
                        <i class="ri-error-warning-line"></i>
                        ${result.message}
                    `;
                    retrainStatus.className = 'retrain-status error';
                }
                
                // Reset the form
                form.reset();
                fileLabel.textContent = 'Choose Dataset File';
                
            } catch (error) {
                retrainStatus.innerHTML = `
                    <i class="ri-error-warning-line"></i>
                    An error occurred during retraining
                `;
                retrainStatus.className = 'retrain-status error';
                console.error('Error:', error);
            } finally {
                loadingIndicator.style.display = 'none';
                retrainStatus.style.display = 'flex';
            }
        });
    }
});