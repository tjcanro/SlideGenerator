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
        
        // Debug: Check if all elements are found
        console.log('Form elements found:', {
            form: !!this.form,
            promptInput: !!this.promptInput,
            submitBtn: !!this.submitBtn,
            clearBtn: !!this.clearBtn,
            status: !!this.status,
            success: !!this.success,
            error: !!this.error
        });
    }

    async init() {
        console.log('Initializing SlideGeneratorApp...');
        
        if (!this.form || !this.submitBtn) {
            console.error('Required elements not found!');
            return;
        }
        
        // Use addEventListener instead of onsubmit for better debugging
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.clearBtn.addEventListener('click', this.clearForm.bind(this));
        this.promptInput.addEventListener('input', this.handleInputChange.bind(this));
        
        // Add fade-in animation to elements
        this.addFadeInAnimation();
        
        // Focus on prompt input
        this.promptInput.focus();
        
        // Test backend connectivity
        await this.testBackendConnection();
        
        console.log('Initialization complete');
    }

    async testBackendConnection() {
        try {
            console.log('Testing backend connection...');
            const response = await fetch('http://localhost:5009/health');
            if (response.ok) {
                const data = await response.json();
                console.log('Backend is running:', data);
            } else {
                console.warn('Backend health check failed:', response.status);
            }
        } catch (error) {
            console.error('Backend connection test failed:', error);
            console.error('Make sure the Flask backend is running on port 5009');
        }
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
        if (this.charCount) {
            this.charCount.textContent = `${charLength} characters`;
        }
        
        // Auto-resize textarea
        this.promptInput.style.height = 'auto';
        this.promptInput.style.height = Math.min(this.promptInput.scrollHeight, 400) + 'px';
    }

    clearForm() {
        console.log('Clearing form...');
        this.promptInput.value = '';
        this.promptInput.style.height = 'auto';
        if (this.charCount) {
            this.charCount.textContent = '0 characters';
        }
        this.hideAllMessages();
        this.promptInput.focus();
        
        // Add a subtle animation
        this.promptInput.classList.add('animate-pulse');
        setTimeout(() => {
            this.promptInput.classList.remove('animate-pulse');
        }, 1000);
    }

    hideAllMessages() {
        if (this.status) this.status.classList.add('hidden');
        if (this.success) this.success.classList.add('hidden');
        if (this.error) this.error.classList.add('hidden');
    }

    showLoading() {
        console.log('Showing loading state...');
        this.hideAllMessages();
        this.status.classList.remove('hidden');
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-3"></i>Generating...';
        this.submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
    }

    showSuccess() {
        console.log('Showing success state...');
        this.hideAllMessages();
        this.success.classList.remove('hidden');
        this.resetSubmitButton();
        
        // Auto-hide success message after 5 seconds
        setTimeout(() => {
            this.success.classList.add('hidden');
        }, 5000);
    }

    showError(message) {
        console.error('Showing error:', message);
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
        console.log('Form submitted');
        e.preventDefault();
        
        const prompt = this.promptInput.value.trim();
        console.log('Prompt:', prompt);
        
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
            console.log('Sending request to:', this.API_URL);
            console.log('Request payload:', { prompt: prompt });
            
            const response = await fetch(this.API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                let errorMessage = 'Failed to generate presentation';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                    console.error('Server error response:', errorData);
                } catch (e) {
                    console.error('Failed to parse error response:', e);
                }
                throw new Error(errorMessage);
            }
            
            const blob = await response.blob();
            console.log('Received blob:', blob.size, 'bytes');
            
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
            console.error('Error in handleSubmit:', error);
            console.error('Error name:', error.name);
            console.error('Error message:', error.message);
            
            // Check if it's a network error
            if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
                this.showError('Cannot connect to server. Please make sure the backend is running on port 5009.');
            } else {
                this.showError(error.message || 'An unexpected error occurred. Please try again.');
            }
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    const app = new SlideGeneratorApp();
    app.init();
});

// Add a global error handler for debugging
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});
