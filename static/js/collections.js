function showCollectionModal(recipeId) {
    const modal = document.getElementById('collection-modal');
    const collectionsList = document.getElementById('collections-list');
    
    // Show loading state
    collectionsList.innerHTML = 'Loading collections...';
    modal.style.display = 'block';

    // Add CSRF token to the request
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/collections/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
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
        if (data.status === 'success') {
            const collections = data.collections;
            if (collections.length === 0) {
                collectionsList.innerHTML = `
                    <p>You don't have any collections yet.</p>
                    <a href="/collections/new/" class="btn btn-primary">Create Collection</a>
                `;
            } else {
                collectionsList.innerHTML = collections.map(collection => `
                    <div class="collection-item">
                        <button onclick="addToCollection(${collection.id}, ${recipeId})" 
                                class="btn btn-secondary">
                            ${collection.name}
                        </button>
                    </div>
                `).join('');
            }
        } else {
            throw new Error(data.message || 'Failed to load collections');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        collectionsList.innerHTML = `
            <p>Error loading collections. Please try again.</p>
            <p>Error details: ${error.message}</p>
        `;
    });
}

function addToCollection(collectionId, recipeId) {
    fetch(`/recipes/collections/${collectionId}/add/${recipeId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Recipe added to collection!');
            document.getElementById('collection-modal').style.display = 'none';
        } else {
            alert(data.message || 'Failed to add recipe to collection');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add recipe to collection');
    });
}

function removeFromCollection(collectionId, recipeId) {
    if (confirm('Are you sure you want to remove this recipe from the collection?')) {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/collections/${collectionId}/remove/${recipeId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Remove the recipe card from the DOM
                const recipeCard = document.getElementById(`recipe-${recipeId}`);
                if (recipeCard) {
                    recipeCard.remove();
                }
                location.reload(); // Refresh the page to update the collection
            } else {
                alert(data.message || 'Failed to remove recipe from collection');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to remove recipe from collection');
        });
    }
}

// Close modal when clicking the X
document.querySelector('.close').onclick = function() {
    document.getElementById('collection-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('collection-modal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
