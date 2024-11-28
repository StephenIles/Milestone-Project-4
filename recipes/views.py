from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta, date
from .forms import UserRegistrationForm, RecipeForm, RatingForm, CommentForm, RecipeSearchForm, CollectionForm
from .models import (
    Recipe, Rating, Comment, Category, Favorite, Tag, 
    ShareCount, Collection, MealPlan, WeeklyMealPlan, UserProfile
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib.auth.models import User

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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

@login_required
def meal_planner(request):
    if not request.user.userprofile.is_premium:
        messages.error(request, 'Meal planning is a premium feature. Please upgrade to access.')
        return redirect('recipes:home')
    
    # Get or create this week's meal plan
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    weekly_plan, created = WeeklyMealPlan.objects.get_or_create(
        user=request.user,
        start_date=start_of_week,
        end_date=end_of_week
    )
    
    # Get daily plans for the week
    daily_plans = {}
    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            date=current_date,
            defaults={'notes': ''}
        )
        daily_plans[current_date] = plan
        if created:
            weekly_plan.daily_plans.add(plan)
    
    # Get ALL recipes, not just user's recipes
    recipes = Recipe.objects.all()  # Changed this line to get all recipes
    
    context = {
        'weekly_plan': weekly_plan,
        'daily_plans': daily_plans,
        'recipes': recipes,
        'shopping_list': weekly_plan.get_weekly_shopping_list()
    }
    
    return render(request, 'recipes/meal_planner.html', context)

@login_required
def update_meal(request, plan_id):
    if not request.user.userprofile.is_premium:
        return JsonResponse({'error': 'Premium feature only'}, status=403)
    
    try:
        plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
        
        if request.method == 'POST':
            data = json.loads(request.body)
            meal_type = data.get('meal_type')
            recipe_id = data.get('recipe_id')
            
            print(f"Updating meal: {meal_type} with recipe: {recipe_id}")  # Debug print
            
            if recipe_id:
                recipe = get_object_or_404(Recipe, id=recipe_id)
                if meal_type == 'breakfast':
                    plan.breakfast = recipe
                elif meal_type == 'lunch':
                    plan.lunch = recipe
                elif meal_type == 'dinner':
                    plan.dinner = recipe
            else:
                if meal_type == 'breakfast':
                    plan.breakfast = None
                elif meal_type == 'lunch':
                    plan.lunch = None
                elif meal_type == 'dinner':
                    plan.dinner = None
            
            plan.save()
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    except Exception as e:
        print(f"Error updating meal: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def shopping_list(request, weekly_plan_id):
    if not request.user.userprofile.is_premium:
        messages.error(request, 'Shopping list is a premium feature. Please upgrade to access.')
        return redirect('recipes:home')
    
    weekly_plan = get_object_or_404(WeeklyMealPlan, id=weekly_plan_id, user=request.user)
    shopping_list = weekly_plan.get_weekly_shopping_list()
    
    return render(request, 'recipes/shopping_list.html', {
        'weekly_plan': weekly_plan,
        'shopping_list': shopping_list
    })

@login_required
def download_shopping_list(request, weekly_plan_id):
    if not request.user.userprofile.is_premium:
        messages.error(request, 'Shopping list download is a premium feature. Please upgrade to access.')
        return redirect('recipes:meal_planner')
    
    try:
        weekly_plan = get_object_or_404(WeeklyMealPlan, id=weekly_plan_id, user=request.user)
        shopping_list = weekly_plan.get_weekly_shopping_list()
        
        # Create the PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = Paragraph(
            f"Shopping List for Week of {weekly_plan.start_date.strftime('%B %d, %Y')}",
            styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        if shopping_list:
            # Create table data
            data = [['Ingredient', 'Quantity', 'Unit']]
            for ingredient, details in shopping_list.items():
                data.append([
                    ingredient,
                    str(details['quantity']),
                    details['unit']
                ])
            
            # Create table
            table = Table(data, colWidths=[250, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No items in shopping list", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # FileResponse
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create the HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="shopping_list_{weekly_plan.start_date.strftime("%Y-%m-%d")}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")  # For debugging
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect('recipes:meal_planner')

@login_required
def download_shopping_list_pdf(request, weekly_plan_id):
    try:
        if not request.user.userprofile.is_premium:
            messages.error(request, 'PDF download is a premium feature. Please upgrade to access.')
            return redirect('recipes:meal_planner')
        
        weekly_plan = get_object_or_404(WeeklyMealPlan, id=weekly_plan_id, user=request.user)
        shopping_list = weekly_plan.get_weekly_shopping_list()
        
        # Create the PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create the elements list to hold all PDF elements
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title = Paragraph(
            f"Shopping List for Week of {weekly_plan.start_date.strftime('%B %d, %Y')}",
            styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Create table data
        if shopping_list:
            data = [['Ingredient', 'Quantity', 'Unit']]
            for ingredient, details in shopping_list.items():
                data.append([
                    ingredient,
                    str(details['quantity']),
                    details['unit']
                ])
            
            # Create table
            table = Table(data, colWidths=[250, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No items in shopping list", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # FileResponse
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create the HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="shopping_list_{weekly_plan.start_date.strftime("%Y-%m-%d")}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")  # For debugging
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect('recipes:meal_planner')

def subscription_page(request):
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'monthly_price_id': settings.STRIPE_MONTHLY_PLAN_ID,
        'yearly_price_id': settings.STRIPE_YEARLY_PLAN_ID
    }
    print("Context:", context)  # Debug print
    return render(request, 'recipes/subscription.html', context)

def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            
            print(f"Creating checkout session for user: {request.user.id}")  # Debug print
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': plan_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(reverse('recipes:subscription_success')),
                cancel_url=request.build_absolute_uri(reverse('recipes:subscription')),
                client_reference_id=str(request.user.id),  # This is important for the webhook
            )
            
            print(f"Created checkout session: {checkout_session.id}")  # Debug print
            return JsonResponse({
                'id': checkout_session.id,
                'url': checkout_session.url
            })
            
        except Exception as e:
            print(f"Error creating checkout session: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def stripe_webhook(request):
    print("\n=== Webhook Received ===")  # Debug print
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print(f"Event Type: {event.type}")  # Debug print
        
        if event.type == 'checkout.session.completed':
            session = event.data.object
            print(f"Session ID: {session.id}")
            print(f"Client Reference ID: {session.client_reference_id}")
            
            try:
                user = User.objects.get(id=session.client_reference_id)
                print(f"Found user: {user.username}")
                
                # Check current premium status
                print(f"Current premium status: {user.userprofile.is_premium}")
                
                # Update premium status
                user.userprofile.is_premium = True
                user.userprofile.save()
                
                # Verify the update
                user.refresh_from_db()
                print(f"New premium status: {user.userprofile.is_premium}")
                print(f"Successfully updated {user.username} to premium!")
                
            except User.DoesNotExist:
                print(f"User not found with ID: {session.client_reference_id}")
            except Exception as e:
                print(f"Error updating user profile: {str(e)}")
                print(f"Error type: {type(e)}")
                
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    return HttpResponse(status=200)

def subscription_success(request):
    return render(request, 'recipes/subscription_success.html')

def subscription_cancel(request):
    return render(request, 'your_template.html')

@login_required
def check_premium_status(request):
    return JsonResponse({
        'is_premium': request.user.userprofile.is_premium,
        'username': request.user.username
    })
