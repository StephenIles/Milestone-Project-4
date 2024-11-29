document.addEventListener('DOMContentLoaded', function() {
    const ingredientsContainer = document.getElementById('ingredients-container');
    const addIngredientButton = document.getElementById('add-ingredient');
    const form = document.getElementById('recipeForm');

    function addIngredientField(name = '', quantity = '', unit = '') {
        const ingredientDiv = document.createElement('div');
        ingredientDiv.className = 'ingredient-entry';
        
        ingredientDiv.innerHTML = `
            <input type="text" class="ingredient-name" placeholder="Ingredient name" value="${name}">
            <input type="text" class="ingredient-quantity" placeholder="Quantity" value="${quantity}">
            <input type="text" class="ingredient-unit" placeholder="Unit" value="${unit}">
            <button type="button" class="btn btn-danger remove-ingredient">
                <i class="fas fa-trash"></i> Remove
            </button>
        `;
        
        ingredientsContainer.appendChild(ingredientDiv);

        // Add remove button functionality
        const removeButton = ingredientDiv.querySelector('.remove-ingredient');
        removeButton.addEventListener('click', () => {
            ingredientDiv.remove();
            updateIngredientsJson();
        });

        // Add change listeners
        const inputs = ingredientDiv.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', updateIngredientsJson);
        });
    }

    function updateIngredientsJson() {
        const ingredients = {};
        document.querySelectorAll('.ingredient-entry').forEach(entry => {
            const name = entry.querySelector('.ingredient-name').value.trim();
            const quantity = entry.querySelector('.ingredient-quantity').value.trim();
            const unit = entry.querySelector('.ingredient-unit').value.trim();
            
            if (name) {
                ingredients[name] = {
                    quantity: quantity,
                    unit: unit
                };
            }
        });
        
        document.querySelector('input[name="ingredients_json"]').value = JSON.stringify(ingredients);
    }

    // Add ingredient button click handler
    if (addIngredientButton) {
        addIngredientButton.addEventListener('click', () => {
            addIngredientField();
            updateIngredientsJson();
        });
    }

    // Add form submit handler
    if (form) {
        form.addEventListener('submit', function(e) {
            const ingredients = document.querySelector('input[name="ingredients_json"]').value;
            if (!ingredients || ingredients === '{}') {
                e.preventDefault();
                alert('Please add at least one ingredient.');
            }
        });
    }

    // Add initial empty ingredient field if container is empty
    if (ingredientsContainer && ingredientsContainer.children.length === 0) {
        addIngredientField();
    }

    // Initial update of ingredients JSON
    updateIngredientsJson();
}); 