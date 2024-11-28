let currentPlanId = null;
let currentMealType = null;

function showRecipeModal(planId, mealType) {
    console.log('Opening modal for plan:', planId, 'meal type:', mealType);
    currentPlanId = planId;
    currentMealType = mealType;
    const modal = document.getElementById('recipe-modal');
    modal.style.display = 'block';
}

function selectRecipe(planId, mealType, recipeId) {
    console.log('Selecting recipe:', recipeId, 'for plan:', planId, 'meal type:', mealType);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/meal-planner/update/${planId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            meal_type: mealType,
            recipe_id: recipeId
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.status === 'success') {
            window.location.reload();
        } else {
            alert(data.message || 'Failed to update meal plan');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update meal plan');
    });

    document.getElementById('recipe-modal').style.display = 'none';
}

function removeMeal(planId, mealType) {
    if (confirm('Are you sure you want to remove this meal?')) {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/meal-planner/update/${planId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                meal_type: mealType,
                recipe_id: null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();  // Refresh to show updated meal plan
            } else {
                alert(data.message || 'Failed to remove meal');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to remove meal');
        });
    }
}

function updateNotes(planId, notes) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/meal-planner/update/${planId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            notes: notes
        })
    })
    .catch(error => console.error('Error updating notes:', error));
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('recipe-modal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking X
document.querySelector('.close').onclick = function() {
    document.getElementById('recipe-modal').style.display = 'none';
}

// Add this to check if JavaScript is loading
console.log('Meal planner JavaScript loaded');