from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, RecipeForm, RatingForm, CommentForm, RecipeSearchForm, CollectionForm
from .models import Recipe, Rating, Comment, Category, Favorite, Tag, ShareCount, Collection

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
    is_favorited = False

    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()


    
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
        'comments': recipe.comments.all(),
        'is_favorited': is_favorited
    }
    return render(request, 'recipes/recipe_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
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

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('recipes:home')

def category_list(request):
    categories = Category.objects.annotate(
        recipe_count=Count('recipes')
    )
    return render(request, 'recipes/category_list.html', {
        'categories': categories
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    recipes = category.recipes.all()
    return render(request, 'recipes/category_detail.html', {
        'category': category,
        'recipes': recipes
    })

@require_POST
@login_required
def toggle_favorite(request, recipe_id):
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()
        
        if favorite:
            favorite.delete()
            return JsonResponse({'status': 'removed'})
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'status': 'added'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def favorite_recipes(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'recipes/favorite_list.html', {
        'favorites': favorites
    })

def tag_list(request):
    tags = Tag.objects.annotate(
        recipe_count=Count('recipes')
    ).order_by('-recipe_count')
    return render(request, 'recipes/tag_list.html', {'tags': tags})

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    recipes = tag.recipes.all()
    return render(request, 'recipes/tag_detail.html', {
        'tag': tag,
        'recipes': recipes
    })

def recipe_search(request):
    form = RecipeSearchForm(request.GET)
    recipes = Recipe.objects.all()
    
    if form.is_valid():
        # Search query
        q = form.cleaned_data.get('q')
        if q:
            recipes = recipes.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(ingredients__icontains=q)
            )
        
        # Category filter
        category = form.cleaned_data.get('category')
        if category:
            recipes = recipes.filter(category=category)
        
        # Tags filter
        tags = form.cleaned_data.get('tags')
        if tags:
            recipes = recipes.filter(tags__in=tags).distinct()
        
        # Cooking time filter
        cooking_time = form.cleaned_data.get('cooking_time')
        if cooking_time:
            recipes = recipes.filter(cooking_time__lte=cooking_time)
        
        # Rating filter
        rating = form.cleaned_data.get('rating')
        if rating:
            recipes = recipes.annotate(
                avg_rating=Avg('ratings__value')
            ).filter(avg_rating__gte=rating)
    
    # Annotate with average rating for display
    recipes = recipes.annotate(
        avg_rating=Avg('ratings__value')
    )
    
    context = {
        'form': form,
        'recipes': recipes,
        'search_query': request.GET.get('q', ''),
    }
    
    return render(request, 'recipes/search.html', context)

def track_share(request, recipe_id, platform):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        share_count, _ = ShareCount.objects.get_or_create(
            recipe=recipe,
            platform=platform
        )
        share_count.count += 1
        share_count.save()
        return JsonResponse({'status': 'success', 'count': share_count.count})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def collection_list(request):
    collections = Collection.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    ).distinct()
    
    can_create = Collection.can_create_collection(request.user)
    
    return render(request, 'recipes/collection_list.html', {
        'collections': collections,
        'can_create': can_create,
    })

@login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if not collection.is_public and collection.owner != request.user:
        raise PermissionDenied
    
    can_add = collection.can_add_recipe(request.user)
    
    return render(request, 'recipes/collection_detail.html', {
        'collection': collection,
        'can_add': can_add,
    })

@login_required
def collection_create(request):
    if not Collection.can_create_collection(request.user):
        messages.error(request, 'You have reached the maximum number of collections for free accounts.')
        return redirect('recipes:collection_list')
    
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            messages.success(request, 'Collection created successfully!')
            return redirect('recipes:collection_detail', pk=collection.pk)
    else:
        form = CollectionForm()
    
    return render(request, 'recipes/collection_form.html', {'form': form})

@login_required
def collection_edit(request, pk):
    collection = get_object_or_404(Collection, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection updated successfully!')
            return redirect('recipes:collection_detail', pk=collection.pk)
    else:
        form = CollectionForm(instance=collection)
    
    return render(request, 'recipes/collection_form.html', {
        'form': form,
        'collection': collection,
    })

@login_required
def collection_delete(request, pk):
    try:
        collection = get_object_or_404(Collection, pk=pk, owner=request.user)
        collection.delete()
        messages.success(request, 'Collection deleted successfully!')
        return redirect('recipes:collection_list')
    except Exception as e:
        messages.error(request, f'Error deleting collection: {str(e)}')
        return redirect('recipes:collection_detail', pk=pk)

@login_required
def collection_add_recipe(request, collection_pk, recipe_pk):
    try:
        collection = get_object_or_404(Collection, pk=collection_pk, owner=request.user)
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        
        if not collection.can_add_recipe(request.user):
            return JsonResponse({
                'status': 'error',
                'message': 'You have reached the maximum recipes for this collection. Upgrade to add more!'
            }, status=400)
        
        collection.recipes.add(recipe)
        return JsonResponse({
            'status': 'success',
            'message': 'Recipe added to collection successfully!'
        })
    except Exception as e:
        print(f"Error adding recipe to collection: {str(e)}")  # For debugging
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def collection_remove_recipe(request, collection_pk, recipe_pk):
    try:
        collection = get_object_or_404(Collection, pk=collection_pk, owner=request.user)
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        
        collection.recipes.remove(recipe)
        return JsonResponse({
            'status': 'success',
            'message': 'Recipe removed from collection successfully!'
        })
    except Exception as e:
        print(f"Error removing recipe from collection: {str(e)}")  # For debugging
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_user_collections(request):
    try:
        collections = Collection.objects.filter(owner=request.user).values('id', 'name')
        return JsonResponse({
            'status': 'success',
            'collections': list(collections)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
