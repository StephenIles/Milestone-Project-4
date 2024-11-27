function toggleFavorite(button) {
    const recipeId = button.dataset.recipeId;
    console.log('Toggling favorite for recipe:', recipeId);
    
    fetch(`/recipes/favorite/${recipeId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Data:', data);
        if (data.status === 'added') {
            button.classList.add('active');
            button.innerHTML = '★ Favorited';
        } else {
            button.classList.remove('active');
            button.innerHTML = '☆ Add to Favorites';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

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