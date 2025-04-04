document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.upload-form');
    const fileInput = document.getElementById('dataset-upload');
    const fileLabel = document.querySelector('.file-upload-label span');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const retrainStatus = document.getElementById('retrainStatus');
    
    // Update file label
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            fileLabel.textContent = this.files.length > 0 
                ? this.files[0].name 
                : 'Choose Dataset File';
        });
    }
    
    // Handle form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showStatus('Please select a dataset file first', 'error');
                return;
            }
            
            loadingIndicator.style.display = 'flex';
            retrainStatus.style.display = 'none';
            
            try {
                const formData = new FormData(form);
                
                const response = await fetch('/retrain', {
                    method: 'POST',
                    body: formData,
                });
                
                if (!response.ok) {
                    const error = await response.json().catch(() => ({ error: 'Server error' }));
                    throw new Error(error.message || error.error || 'Server error');
                }
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showStatus(result.message, 'success', result.metrics);
                } else {
                    showStatus(result.error || 'Retraining failed', 'error');
                }
                
            } catch (error) {
                console.error('Retrain error:', error);
                showStatus(
                    error.message || 'An error occurred during retraining', 
                    'error'
                );
            } finally {
                loadingIndicator.style.display = 'none';
                retrainStatus.style.display = 'flex';
                
                if (retrainStatus.classList.contains('success')) {
                    form.reset();
                    fileLabel.textContent = 'Choose Dataset File';
                }
            }
        });
    }
    
    function showStatus(message, status, metrics = null) {
        let metricsHtml = '';
        
        if (metrics) {
            metricsHtml = `
                <div class="status-container">
                    <div class="status-header">
                        <i class="ri-${status === 'success' ? 'checkbox-circle-line' : 'error-warning-line'}"></i>
                        <div class="status-title">${message}</div>
                    </div>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="metric-label">Accuracy</span>
                            <span class="metric-value">${metrics.accuracy}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Precision</span>
                            <span class="metric-value">${metrics.precision}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Recall</span>
                            <span class="metric-value">${metrics.recall}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">F1 Score</span>
                            <span class="metric-value">${metrics.f1_score}</span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            metricsHtml = `
                <div class="status-container">
                    <div class="status-header">
                        <i class="ri-${status === 'success' ? 'checkbox-circle-line' : 'error-warning-line'}"></i>
                        <div class="status-title">${message}</div>
                    </div>
                </div>
            `;
        }
        
        retrainStatus.innerHTML = metricsHtml;
        retrainStatus.className = `retrain-status ${status}`;
    }
});