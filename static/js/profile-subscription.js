document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded');
    
    const cancelButton = document.querySelector('.btn-cancel');
    console.log('Cancel button found:', cancelButton);
    
    if (cancelButton) {
        cancelButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Cancel button clicked');
            
            if (confirm('Are you sure you want to cancel your subscription? This action cannot be undone.')) {
                fetch('/recipes/cancel-subscription/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    console.log('Response status:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Response data:', data);
                    
                    if (data.success) {
                        // Update status badge
                        const statusBadge = document.querySelector('.status-badge');
                        if (statusBadge) {
                            statusBadge.textContent = 'Cancelled';
                            statusBadge.classList.remove('active');
                            statusBadge.classList.add('cancelled');
                        }

                        // Update plan container
                        const currentPlan = document.querySelector('.current-plan');
                        if (currentPlan) {
                            currentPlan.classList.add('cancelled');
                        }

                        // Remove cancel button
                        cancelButton.remove();

                        // Show success message
                        alert('Subscription cancelled successfully');
                    } else {
                        throw new Error(data.error || 'Failed to cancel subscription');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to cancel subscription: ' + error.message);
                });
            }
        });
    }
}); 