document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');
  const modal = document.getElementById('resultModal');
  const predictionResult = document.getElementById('predictionResult');
  const closeModalBtns = document.querySelectorAll('.close-modal, .close-modal-btn');
  const predictAgainBtn = document.querySelector('.predict-again');
  const loadingIndicator = document.getElementById('loadingIndicator');
  
  if (form) {
      form.addEventListener('submit', async function(e) {
          e.preventDefault();
          loadingIndicator.style.display = 'flex';
          
          try {
              const formData = new FormData(form);
              const response = await fetch('/predict', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/x-www-form-urlencoded',
                  },
                  body: new URLSearchParams(formData)
              });
              
              const data = await response.json();
              
              if (data.error) {
                  throw new Error(data.error);
              }
              
              predictionResult.innerHTML = `
                  <strong>Result:</strong> ${data.message}<br><br>
                  <i class="${data.result === 1 ? 'ri-alarm-warning-line' : 'ri-heart-line'}"></i>
                  ${data.result === 1 ? 'Please consult a healthcare professional.' : 'Maintain your healthy habits!'}
                  ${data.probability ? `<br><small>Probability: ${(data.probability * 100).toFixed(1)}%</small>` : ''}
              `;
              
              modal.style.display = 'block';
              
          } catch (error) {
              alert('Error: ' + error.message);
          } finally {
              loadingIndicator.style.display = 'none';
          }
      });
  }
  
  closeModalBtns.forEach(btn => {
      btn.addEventListener('click', function() {
          modal.style.display = 'none';
      });
  });
  
  predictAgainBtn.addEventListener('click', function() {
      modal.style.display = 'none';
      form.reset();
  });
  
  window.addEventListener('click', function(e) {
      if (e.target === modal) {
          modal.style.display = 'none';
      }
  });
});
