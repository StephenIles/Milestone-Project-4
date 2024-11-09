from django.shortcuts import render
from .models import Recipe

def home(request):
    latest_recipes = Recipe.objects.all()  # Get all recipes for now
    return render(request, 'recipes/home.html', {'latest_recipes': latest_recipes})

def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    
    # Access specific ingredient
    flour_details = recipe.ingredients.get('flour', {})
    flour_quantity = flour_details.get('quantity')
    flour_unit = flour_details.get('unit')
    
    # Get all ingredients formatted
    ingredients_list = recipe.get_ingredients_list()
    
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'ingredients_list': ingredients_list
    })
