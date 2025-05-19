// Wellness Agent Frontend JavaScript

document.addEventListener('DOMContentLoaded', () => {
  // Element selectors
  const navLinks = document.querySelectorAll('.nav-link[data-page]');
  const pageContents = document.querySelectorAll('.page-content');
  const pageTitle = document.querySelector('.page-title');
  const chatInput = document.querySelector('.chat-input input');
  const sendButton = document.querySelector('.send-button');
  const messagesContainer = document.querySelector('.messages');
  const emojiOptions = document.querySelectorAll('.emoji-option');
  
  // Initialize charts
  initCharts();
  
  // Page navigation
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Get the target page
      const targetPage = link.getAttribute('data-page');
      
      // Update active nav link
      navLinks.forEach(navLink => navLink.classList.remove('active'));
      link.classList.add('active');
      
      // Show target page content
      pageContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === targetPage) {
          content.classList.add('active');
          // Update page title
          pageTitle.textContent = link.textContent.trim();
        }
      });
    });
  });
  
  // Chat functionality
  if (sendButton && chatInput) {
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  }
  
  // Emoji selection in daily check-in
  if (emojiOptions) {
    emojiOptions.forEach(option => {
      option.addEventListener('click', () => {
        // Remove selected class from all options
        emojiOptions.forEach(opt => opt.classList.remove('selected'));
        // Add selected class to clicked option
        option.classList.add('selected');
      });
    });
  }
  
  // Function to send chat message
  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Send to backend API (simulated for now)
    setTimeout(() => {
      // Simulate response from the wellness agent
      getAgentResponse(message);
    }, 500);
  }
  
  // Function to add message to chat
  function addMessageToChat(content, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.textContent = content;
    
    messagesContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  // Simulate agent response (will be replaced with actual API call)
  function getAgentResponse(userMessage) {
    // Simple simulation of responses
    let response;
    
    if (userMessage.toLowerCase().includes('help')) {
      response = "I can help you track your wellness, request accommodations, or provide resources. What would you like to do?";
    } else if (userMessage.toLowerCase().includes('symptom') || userMessage.toLowerCase().includes('sick')) {
      response = "I'm sorry to hear that. Would you like to log your symptoms or request time off?";
    } else if (userMessage.toLowerCase().includes('request') || userMessage.toLowerCase().includes('accommodation')) {
      response = "To request an accommodation, please go to the Employee Portal and click on 'New Request'. Would you like me to help you with that?";
    } else if (userMessage.toLowerCase().includes('policy') || userMessage.toLowerCase().includes('policies')) {
      response = "You can view your company's wellness policies in the HR Portal. Would you like me to show you where?";
    } else {
      response = "I understand you're interested in wellness support. How can I assist you today?";
    }
    
    // Add response to chat
    addMessageToChat(response, 'system');
    
    // In a real implementation, we would make an API call like this:
    /*
    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messages: [
          { role: "user", content: userMessage }
        ]
      })
    })
    .then(response => response.json())
    .then(data => {
      addMessageToChat(data.response, 'system');
    })
    .catch(error => {
      console.error('Error chatting with agent:', error);
      addMessageToChat("I'm sorry, I'm having trouble connecting. Please try again later.", 'system');
    });
    */
  }
  
  // Initialize charts
  function initCharts() {
    // Trends chart for HR
    const trendsChart = document.getElementById('trendsChart');
    if (trendsChart) {
      new Chart(trendsChart, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Wellness Score',
            data: [75, 72, 78, 77, 80, 82],
            borderColor: '#007bff',
            tension: 0.1,
            fill: false
          }, {
            label: 'Accommodation Requests',
            data: [12, 15, 10, 8, 9, 7],
            borderColor: '#6f42c1',
            tension: 0.1,
            fill: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
    
    // Organization health chart for employer
    const orgHealthChart = document.getElementById('orgHealthChart');
    if (orgHealthChart) {
      new Chart(orgHealthChart, {
        type: 'bar',
        data: {
          labels: ['Q1', 'Q2', 'Q3', 'Q4'],
          datasets: [{
            label: 'Wellness Score',
            data: [72, 75, 78, 82],
            backgroundColor: 'rgba(0, 123, 255, 0.5)',
            borderColor: 'rgb(0, 123, 255)',
            borderWidth: 1
          }, {
            label: 'Productivity Index',
            data: [68, 72, 75, 80],
            backgroundColor: 'rgba(40, 167, 69, 0.5)',
            borderColor: 'rgb(40, 167, 69)',
            borderWidth: 1
          }, {
            label: 'Absence Rate',
            data: [15, 12, 9, 7],
            backgroundColor: 'rgba(220, 53, 69, 0.5)',
            borderColor: 'rgb(220, 53, 69)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  }
  
  // API connectivity (for future implementation)
  function checkApiStatus() {
    fetch('/api/health')
      .then(response => response.json())
      .then(data => {
        if (data.status === 'ok') {
          console.log('Connected to Wellness Agent API');
        } else {
          console.warn('API connection issues');
        }
      })
      .catch(error => {
        console.error('API not available:', error);
      });
  }
  
  // Check API status on load
  checkApiStatus();
}); 