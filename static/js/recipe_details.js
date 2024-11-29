document.addEventListener('DOMContentLoaded', function() {
    // Handle favorite button clicks
    const favoriteBtn = document.querySelector('.favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function() {
            const recipeId = this.dataset.recipe;
            fetch(`/recipes/${recipeId}/favorite/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Toggle button appearance
                    this.innerHTML = data.is_favorite ? 
                        '<i class="fas fa-heart"></i> Remove from Favorites' :
                        '<i class="far fa-heart"></i> Add to Favorites';
                    this.classList.toggle('btn-primary');
                    this.classList.toggle('btn-danger');
                }
            });
        });
    }

    // Handle delete button
    const deleteBtn = document.querySelector('.delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this recipe?')) {
                const recipeId = this.dataset.recipe;
                fetch(`/recipes/${recipeId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/recipes/my-recipes/';
                    }
                });
            }
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}