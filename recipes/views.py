from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import UserRegistrationForm, RecipeForm, RatingForm, CommentForm
from .models import Recipe, Rating, Comment

def home(request):
    latest_recipes = Recipe.objects.all()  # Get all recipes for now
    return render(request, 'recipes/home.html', {'latest_recipes': latest_recipes})

def recipe_list(request):
    recipes = Recipe.objects.all()
    query = request.GET.get('q')
    cooking_time = request.GET.get('cooking_time')
    servings = request.GET.get('servings')

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        )

    if cooking_time:
        recipes = recipes.filter(cooking_time__lte=cooking_time)

    if servings:
        recipes = recipes.filter(servings=servings)

    context = {
        'recipes': recipes,
        'query': query,
        'cooking_time': cooking_time,
        'servings': servings,
    }
    return render(request, 'recipes/recipe_list.html', context)

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user_rating = None
    rating_form = None
    comment_form = None
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(recipe=recipe, user=request.user).first()
        rating_form = RatingForm(instance=user_rating)
        comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'rating' in request.POST:
            rating_form = RatingForm(request.POST, instance=user_rating)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.recipe = recipe
                rating.user = request.user
                rating.save()
                messages.success(request, 'Rating submitted successfully!')
                return redirect('recipes:recipe_detail', pk=pk)
                
        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.recipe = recipe
                comment.user = request.user
                comment.save()
                messages.success(request, 'Comment added successfully!')
                return redirect('recipes:recipe_detail', pk=pk)

    context = {
        'recipe': recipe,
        'user_rating': user_rating,
        'rating_form': rating_form,
        'comment_form': comment_form,
        'comments': recipe.comments.all()
    }
    return render(request, 'recipes/recipe_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    user_recipes = Recipe.objects.filter(author=request.user)
    return render(request, 'recipes/profile.html', {'recipes': user_recipes})

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            messages.success(request, 'Recipe created successfully!')
            return redirect('recipes:recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form, 'title': 'Create Recipe'})

@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, 'Recipe updated successfully!')
            return redirect('recipes:recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form, 'title': 'Edit Recipe'})

@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully!')
        return redirect('recipes:profile')
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})
