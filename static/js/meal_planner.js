document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('recipeModal');
    const modalClose = document.querySelector('.modal-close');
    const recipeSearch = document.getElementById('recipeSearch');
    const recipeList = document.getElementById('recipeList');
    let currentButton = null;

    // Add click handlers to all add recipe buttons
    document.querySelectorAll('.add-recipe-btn').forEach(button => {
        button.addEventListener('click', function() {
            currentButton = this;
            modal.style.display = 'block';
            loadRecipes('');
            recipeSearch.focus();
        });
    });

    // Close modal when clicking X
    modalClose.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Search functionality
    let searchTimeout;
    recipeSearch.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadRecipes(this.value);
        }, 300);
    });

    function loadRecipes(searchQuery) {
        fetch(`/api/recipes/search/?q=${encodeURIComponent(searchQuery)}`)
            .then(response => response.json())
            .then(data => {
                recipeList.innerHTML = '';
                data.forEach(recipe => {
                    const recipeItem = document.createElement('div');
                    recipeItem.className = 'recipe-item';
                    recipeItem.innerHTML = `
                        <h4>${recipe.title}</h4>
                        <p>${recipe.cooking_time} mins</p>
                    `;
                    recipeItem.addEventListener('click', () => {
                        addRecipeToMealPlan(recipe.id);
                    });
                    recipeList.appendChild(recipeItem);
                });
            });
    }

    function addRecipeToMealPlan(recipeId) {
        const planId = currentButton.closest('.day-card').dataset.planId;
        const mealType = currentButton.dataset.mealType;

        fetch('/api/meal-planner/add-meal/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                recipe_id: recipeId,
                meal_type: mealType,
                plan_id: planId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const mealSlot = currentButton.closest('.meal-slot');
                mealSlot.innerHTML = `
                    <h4>${mealType.charAt(0).toUpperCase() + mealType.slice(1)}</h4>
                    <div class="meal-recipe">
                        <h5>${data.recipe.title}</h5>
                        <p>${data.recipe.cooking_time} mins</p>
                        <button class="remove-recipe-btn" onclick="removeMeal(${planId}, '${mealType}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
                modal.style.display = 'none';
            }
        });
    }
});

// Global removeMeal function
window.removeMeal = function(planId, mealType) {
    if (!confirm('Are you sure you want to remove this meal?')) {
        return;
    }

    fetch('/api/meal-planner/remove-meal/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            plan_id: planId,
            meal_type: mealType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const mealSlot = document.querySelector(`[data-plan-id="${planId}"] .meal-slot[data-meal-type="${mealType}"]`);
            mealSlot.innerHTML = `
                <h4>${mealType.charAt(0).toUpperCase() + mealType.slice(1)}</h4>
                <button class="add-recipe-btn" data-meal-type="${mealType}" data-date="${data.date}">
                    <i class="fas fa-plus"></i> Add ${mealType.charAt(0).toUpperCase() + mealType.slice(1)}
                </button>
            `;
            
            // Reinitialize click handler for the new button
            const newButton = mealSlot.querySelector('.add-recipe-btn');
            if (newButton) {
                newButton.addEventListener('click', function() {
                    const modal = document.getElementById('recipeModal');
                    currentButton = this;
                    modal.style.display = 'block';
                    loadRecipes('');
                    document.getElementById('recipeSearch').focus();
                });
            }
        }
    });
}; 