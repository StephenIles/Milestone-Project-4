document.addEventListener('DOMContentLoaded', function() {
    // Delete recipe functionality
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recipeId = this.dataset.recipe;
            
            if (confirm('Are you sure you want to delete this recipe? This action cannot be undone.')) {
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Send delete request
                fetch(`/recipe/${recipeId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message
                        const message = document.createElement('div');
                        message.className = 'alert alert-success';
                        message.textContent = 'Recipe deleted successfully!';
                        document.body.insertBefore(message, document.body.firstChild);
                        
                        // Redirect after a short delay
                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 1000);
                    } else {
                        throw new Error(data.error || 'Failed to delete recipe');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to delete recipe. Please try again.');
                });
            }
        });
    });
}); 