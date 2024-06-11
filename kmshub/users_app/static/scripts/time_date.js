function updateTime() {
    const now = new Date();
    const timeElement = document.getElementById('current-time');
    const dateElement = document.getElementById('current-date');
    
    const timeString = now.toLocaleTimeString();
    const dateString = now.toDateString();
    
    timeElement.textContent = timeString;
    dateElement.textContent = dateString;
  }
  
  // Update time every second
  setInterval(updateTime, 1000);
  
  // Initial call to display time immediately
  updateTime();
  