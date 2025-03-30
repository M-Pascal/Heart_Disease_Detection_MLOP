// document.addEventListener('DOMContentLoaded', function() {
//     // Counter animation
//     const counterElement = document.getElementById('clientCounter');
//     const targetNumber = 1520;
//     const duration = 2000; // 2 seconds
//     const frameDuration = 1000 / 60; // 60 frames per second
//     const totalFrames = Math.round(duration / frameDuration);
//     const easeOutQuad = t => t * (2 - t);
  
//     let frame = 0;
//     const counter = setInterval(() => {
//       frame++;
//       const progress = easeOutQuad(frame / totalFrames);
//       const currentNumber = Math.round(targetNumber * progress);
      
//       counterElement.textContent = currentNumber.toLocaleString();
      
//       if (frame === totalFrames) {
//         clearInterval(counter);
//       }
//     }, frameDuration);
  
//     // Predict button functionality
//     const predictBtn = document.getElementById('predictBtn');
//     const loadingIndicator = document.getElementById('loadingIndicator');
  
//     predictBtn.addEventListener('click', function() {
//       // Show loading indicator
//       predictBtn.style.display = 'none';
//       loadingIndicator.style.display = 'flex';
      
//       // Simulate API call (replace with actual API call)
//       setTimeout(() => {
//         // Hide loading indicator after 3 seconds (simulated response time)
//         loadingIndicator.style.display = 'none';
//         predictBtn.style.display = 'block';
        
//         // Here you would handle the actual response
//         alert('Prediction completed!'); // Replace with your actual response handling
//       }, 3000);
//     });
//   });
