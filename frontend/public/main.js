class SlideGeneratorApp {
    constructor() {
        this.form = document.querySelector('#form');
        this.promptInput = document.querySelector('#prompt');
        this.submitBtn = document.querySelector('#submitBtn');
        this.clearBtn = document.querySelector('#clearBtn');
        this.status = document.querySelector('#status');
        this.success = document.querySelector('#success');
        this.error = document.querySelector('#error');
        this.errorMessage = document.querySelector('#errorMessage');
        this.charCount = document.querySelector('#charCount');
        this.API_URL = 'http://localhost:5009/generate';
    }

    async init() {
        this.form.onsubmit = this.handleSubmit.bind(this);
        this.clearBtn.onclick = this.clearForm.bind(this);
        this.promptInput.addEventListener('input', this.handleInputChange.bind(this));
        
        // Add fade-in animation to elements
        this.addFadeInAnimation();
        
        // Focus on prompt input
        this.promptInput.focus();
    }

    addFadeInAnimation() {
        const elements = document.querySelectorAll('.fade-in');
        elements.forEach((el, index) => {
            el.style.animationDelay = `${index * 0.1}s`;
        });
    }

    handleInputChange() {
        // Hide any existing messages when user starts typing
        this.hideAllMessages();
        
        // Update character count
        const charLength = this.promptInput.value.length;
        this.charCount.textContent = `${charLength} characters`;
        
        // Auto-resize textarea
        this.promptInput.style.height = 'auto';
        this.promptInput.style.height = Math.min(this.promptInput.scrollHeight, 400) + 'px';
    }

    clearForm() {
        this.promptInput.value = '';
        this.promptInput.style.height = 'auto';
        this.charCount.textContent = '0 characters';
        this.hideAllMessages();
        this.promptInput.focus();
        
        // Add a subtle animation
        this.promptInput.classList.add('animate-pulse');
        setTimeout(() => {
            this.promptInput.classList.remove('animate-pulse');
        }, 1000);
    }

    hideAllMessages() {
        this.status.classList.add('hidden'); this.success.classList.add('hidden'); this.error.classList.add('hidden'); }
    
    showLoading() {
        this.hideAllMessages();
        this.status.classList.remove('hidden');
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-3"></i>Generating...';
        this.submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
    }
    
    showSuccess() {
        this.hideAllMessages();
        this.success.classList.remove('hidden');
        this.resetSubmitButton();
        
        // Auto-hide success message after 5 seconds
        setTimeout(() => {
            this.success.classList.add('hidden');
        }, 5000);
    }
    
    showError(message) {
        this.hideAllMessages();
        this.error.classList.remove('hidden');
        this.errorMessage.textContent = message;
        this.resetSubmitButton();
    }
    
    resetSubmitButton() {
        this.submitBtn.disabled = false;
        this.submitBtn.innerHTML = '<i class="fas fa-magic mr-3"></i>Generate Presentation';
        this.submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const prompt = this.promptInput.value.trim();
        
        if (!prompt) {
            this.showError('Please enter a prompt for your presentation');
            this.promptInput.focus();
            return;
        }
    
        if (prompt.length < 10) {
            this.showError('Please provide a more detailed prompt (at least 10 characters)');
            this.promptInput.focus();
            return;
        }
    
        this.showLoading();
        
        try {
            const response = await fetch(this.API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate presentation');
            }
            
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Generate filename with timestamp
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            a.download = `Presentation_${timestamp}.pptx`;
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showSuccess();
            
            // Optionally clear the form after successful generation
            setTimeout(() => {
                if (confirm('Would you like to create another presentation?')) {
                    this.clearForm();
                }
            }, 2000);
            
        } catch (error) {
            console.error('Error:', error);
            this.showError(error.message || 'An unexpected error occurred. Please try again.');
        }
    }
}        