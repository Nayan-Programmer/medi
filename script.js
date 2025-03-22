document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            document.querySelector(targetId).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Symptoms form character counter
    const symptomsTextarea = document.getElementById('symptoms-textarea');
    const charCounter = document.getElementById('char-counter');
    
    if (symptomsTextarea && charCounter) {
        symptomsTextarea.addEventListener('input', function() {
            const remaining = 1000 - this.value.length;
            charCounter.textContent = `${remaining} characters remaining`;
            
            if (remaining < 100) {
                charCounter.classList.add('text-danger');
            } else {
                charCounter.classList.remove('text-danger');
            }
        });
    }

    // Risk level visualization
    const riskElements = document.querySelectorAll('.risk-level');
    if (riskElements.length > 0) {
        riskElements.forEach(el => {
            const riskLevel = el.dataset.risk;
            
            if (riskLevel === 'high') {
                el.classList.add('bg-danger', 'text-white');
            } else if (riskLevel === 'moderate') {
                el.classList.add('bg-warning');
            } else {
                el.classList.add('bg-success', 'text-white');
            }
        });
    }

    // Chatbot functionality
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (chatbotForm && chatbotInput && chatMessages) {
        chatbotForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userMessage = chatbotInput.value.trim();
            if (!userMessage) return;
            
            // Add user message to chat
            addMessageToChat('user', userMessage);
            
            // Clear input
            chatbotInput.value = '';
            
            // Show thinking indicator
            addThinkingIndicator();
            
            // Send to backend
            fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            })
            .then(response => response.json())
            .then(data => {
                // Remove thinking indicator
                removeThinkingIndicator();
                
                // Add bot response
                addMessageToChat('bot', data.response);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                removeThinkingIndicator();
                addMessageToChat('bot', 'Sorry, there was an error processing your request.');
            });
        });
        
        function addMessageToChat(sender, message) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${sender}-message`, 'mb-3', 'p-3');
            
            const iconClass = sender === 'user' ? 'bi-person-circle' : 'bi-robot';
            
            messageDiv.innerHTML = `
                <div class="d-flex align-items-center mb-1">
                    <i class="bi ${iconClass} me-2"></i>
                    <strong>${sender === 'user' ? 'You' : 'MediBot'}</strong>
                </div>
                <div class="message-content">${message}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function addThinkingIndicator() {
            const indicator = document.createElement('div');
            indicator.id = 'thinking-indicator';
            indicator.classList.add('message', 'bot-message', 'mb-3', 'p-3');
            indicator.innerHTML = `
                <div class="d-flex align-items-center mb-1">
                    <i class="bi bi-robot me-2"></i>
                    <strong>MediBot</strong>
                </div>
                <div class="message-content">
                    <div class="thinking-dots">
                        <span class="dot"></span>
                        <span class="dot"></span>
                        <span class="dot"></span>
                    </div>
                </div>
            `;
            
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function removeThinkingIndicator() {
            const indicator = document.getElementById('thinking-indicator');
            if (indicator) {
                indicator.remove();
            }
        }
    }
});
