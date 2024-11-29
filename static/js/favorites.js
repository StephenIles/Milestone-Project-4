console.log('Debug: favorites.js loading');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Debug: favorites.js DOM Content Loaded');
    
    const favoriteButtons = document.querySelectorAll('.btn-favorite, .btn-remove-favorite');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Button clicked');

            const recipeId = this.dataset.recipeId;
            const isFavorite = this.dataset.isFavorite === 'true';
            const isOnFavoritesPage = this.classList.contains('btn-remove-favorite');

            console.log('Recipe ID:', recipeId);
            console.log('Is Favorite:', isFavorite);
            console.log('Is on Favorites Page:', isOnFavoritesPage);

            // Disable button and show loading state
            this.disabled = true;
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + 
                            (isFavorite ? 'Removing...' : 'Adding...');

            fetch(`/recipe/${recipeId}/favorite/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    action: isFavorite ? 'remove' : 'add'
                })
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                
                if (data.success) {
                    if (isOnFavoritesPage && isFavorite) {
                        // Remove the card with animation on favorites page
                        const card = this.closest('.favorite-card');
                        card.style.animation = 'fadeOut 0.3s ease';
                        setTimeout(() => {
                            card.remove();
                            // Check if there are any favorites left
                            const remainingCards = document.querySelectorAll('.favorite-card');
                            if (remainingCards.length === 0) {
                                location.reload(); // Reload to show empty state
                            }
                        }, 300);
                    } else {
                        // Update button on recipe detail page
                        this.dataset.isFavorite = (!isFavorite).toString();
                        if (!isFavorite) {
                            this.innerHTML = '<i class="fas fa-heart"></i> Remove from Favorites';
                            this.classList.add('is-favorite');
                        } else {
                            this.innerHTML = '<i class="far fa-heart"></i> Add to Favorites';
                            this.classList.remove('is-favorite');
                        }
                    }

                    // Show success message
                    const message = document.createElement('div');
                    message.className = 'alert alert-success';
                    message.textContent = data.message;
                    this.closest('.recipe-detail, .favorites-container').insertAdjacentElement('afterbegin', message);
                    setTimeout(() => message.remove(), 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Reset button state
                this.disabled = false;
                this.innerHTML = originalContent;
                
                // Show error message
                const message = document.createElement('div');
                message.className = 'alert alert-danger';
                message.textContent = 'Failed to update favorites. Please try again.';
                this.closest('.recipe-detail, .favorites-container').insertAdjacentElement('afterbegin', message);
                setTimeout(() => message.remove(), 3000);
            });
        });
    });
});

console.log('Debug: favorites.js loaded');