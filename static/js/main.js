// Add loading states
function showLoading(element) {
    element.classList.add('loading');
    element.innerHTML = '<span class="spinner"></span> Processing...';
}

function hideLoading(element, originalText) {
    element.classList.remove('loading');
    element.innerHTML = originalText;
}

// Add form feedback
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            showLoading(submitBtn);
            
            // Re-enable button after response
            setTimeout(() => hideLoading(submitBtn, originalText), 2000);
        }
    });
});

// Add AJAX feedback for recipe actions
function updateRecipe(recipeId, action) {
    const button = document.querySelector(`[data-recipe="${recipeId}"]`);
    const originalText = button.innerHTML;
    
    showLoading(button);
    
    fetch(`/recipes/${recipeId}/${action}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(button, data.message);
        showFeedback(data.message, data.status);
    })
    .catch(error => {
        hideLoading(button, originalText);
        showFeedback('An error occurred', 'error');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
});