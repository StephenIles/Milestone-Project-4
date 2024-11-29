from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.contrib.auth import logout, login, authenticate
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta, date
from .forms import UserRegistrationForm, RecipeForm, RatingForm, CommentForm, RecipeSearchForm, CollectionForm
from .models import (
    Recipe, Rating, Comment, Category, Favorite, Tag, 
    ShareCount, Collection, MealPlan, WeeklyMealPlan, UserProfile, Subscription, DailyMealPlan
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
from datetime import datetime

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    latest_recipes = Recipe.objects.all().order_by('-created_at')[:6]
    return render(request, 'recipes/home.html', {'latest_recipes': latest_recipes})

def all_recipes(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'recipes/all_recipes.html', {'recipes': recipes})

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

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    is_favorite = False
    
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()
    
    context = {
        'recipe': recipe,
        'is_favorite': is_favorite,
    }
    
    return render(request, 'recipes/recipe_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('recipes:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'recipes/register.html', {'form': form})

@login_required
def profile(request):
    # Check for session ID in URL (after successful payment)
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                # Force refresh the subscription from the database
                subscription = Subscription.objects.filter(user=request.user).first()
                if not subscription:
                    subscription = Subscription.objects.create(
                        user=request.user,
                        plan='free'
                    )
        except Exception as e:
            print(f"Error checking session: {str(e)}")

    # Always get a fresh subscription object
    subscription = Subscription.objects.filter(user=request.user).first()
    if not subscription:
        subscription = Subscription.objects.create(
            user=request.user,
            plan='free'
        )

    # Get user's recipes and favorites
    recipes = Recipe.objects.filter(author=request.user)
    favorites = Favorite.objects.filter(user=request.user)

    context = {
        'user': request.user,
        'recipes': recipes,
        'favorites': favorites,
        'subscription': subscription,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'monthly_price_id': settings.STRIPE_MONTHLY_PRICE_ID,
        'yearly_price_id': settings.STRIPE_YEARLY_PRICE_ID,
    }
    return render(request, 'recipes/profile.html', context)

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            
            # Handle ingredients
            ingredients_json = request.POST.get('ingredients_json', '{}')
            try:
                recipe.ingredients = json.loads(ingredients_json)
            except json.JSONDecodeError:
                recipe.ingredients = {}
            
            recipe.save()
            messages.success(request, 'Recipe created successfully!')
            return redirect('recipes:recipe_detail', recipe.id)
    else:
        form = RecipeForm()
    
    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredients_json = request.POST.get('ingredients_json')
        
        try:
            # Parse and validate ingredients
            if ingredients_json:
                ingredients_data = json.loads(ingredients_json)
                if not ingredients_data:
                    form.add_error(None, 'At least one ingredient is required.')
            else:
                form.add_error(None, 'Ingredients are required.')
                
            if form.is_valid():
                recipe = form.save(commit=False)
                recipe.ingredients = ingredients_data
                recipe.save()
                messages.success(request, 'Recipe updated successfully!')
                return redirect('recipes:recipe_detail', recipe_id=recipe.pk)
                
        except json.JSONDecodeError:
            form.add_error(None, 'Invalid ingredients format.')
            
    else:
        form = RecipeForm(instance=recipe)
        
    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'recipe': recipe,
        'edit_mode': True,
        'initial_ingredients': json.dumps(recipe.ingredients) if recipe.ingredients else '{}'
    })

@login_required
@require_POST
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    try:
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully!')
        return JsonResponse({'success': True, 'redirect_url': reverse('recipes:all_recipes')})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('recipes:home')

def category_list(request):
    categories = Category.objects.annotate(
        recipe_count=Count('recipes')
    ).order_by('name')
    return render(request, 'recipes/category_list.html', {'categories': categories})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    recipes = Recipe.objects.filter(category=category).order_by('-created_at')
    return render(request, 'recipes/category_detail.html', {
        'category': category,
        'recipes': recipes
    })

@login_required
def toggle_favorite(request, recipe_id):
    print("Toggle favorite view called")  # Debug print
    if request.method == 'POST':
        try:
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
            
            # Get the action from the request body
            data = json.loads(request.body)
            action = data.get('action', 'toggle')
            
            print(f"Action: {action}, Recipe: {recipe_id}, User: {request.user}")  # Debug print
            
            if action == 'remove' or (action == 'toggle' and favorite.exists()):
                favorite.delete()
                is_favorite = False
                message = 'Recipe removed from favorites'
            else:
                Favorite.objects.create(user=request.user, recipe=recipe)
                is_favorite = True
                message = 'Recipe added to favorites'
            
            print(f"Operation completed - Is Favorite: {is_favorite}")  # Debug print
            
            return JsonResponse({
                'success': True,
                'message': message,
                'is_favorite': is_favorite
            })
            
        except Exception as e:
            print(f"Error in toggle_favorite: {str(e)}")  # Debug print
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@login_required
def favorite_recipes(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'recipes/favorite_list.html', {
        'favorites': favorites
    })

def tag_list(request):
    """Display list of all tags with recipe counts"""
    tags = Tag.objects.all()
    for tag in tags:
        tag.count = tag.get_recipe_count()
    return render(request, 'recipes/tag_list.html', {'tags': tags})

def tag_detail(request, slug):
    """Display recipes for a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    recipes = Recipe.objects.filter(tags=tag).select_related('author', 'category')
    context = {
        'tag': tag,
        'recipes': recipes,
    }
    return render(request, 'recipes/tag_detail.html', context)

def recipe_search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    tags = request.GET.getlist('tags')
    
    recipes = Recipe.objects.all()
    
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        )
    
    if category:
        recipes = recipes.filter(category__slug=category)
    
    if tags:
        recipes = recipes.filter(tags__slug__in=tags)
    
    # Get categories and tags for filters
    categories = Category.objects.all()
    all_tags = Tag.objects.all()
    
    context = {
        'recipes': recipes.distinct(),
        'query': query,
        'selected_category': category,
        'selected_tags': tags,
        'categories': categories,
        'tags': all_tags,
    }
    
    return render(request, 'recipes/search_results.html', context)

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
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            if Collection.can_create_collection(request.user):
                collection = form.save(commit=False)
                collection.owner = request.user
                collection.save()
                return redirect('recipes:collection_detail', pk=collection.pk)
            else:
                messages.error(request, 'You have reached your collection limit. Upgrade to premium for unlimited collections.')
                return redirect('recipes:collection_list')
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
    # Get or create the current week's meal plan
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    
    weekly_plan, created = WeeklyMealPlan.objects.get_or_create(
        user=request.user,
        start_date=start_of_week
    )
    
    # Create daily plans for the week if they don't exist
    daily_plans = {}
    for i in range(7):
        date = start_of_week + timezone.timedelta(days=i)
        daily_plan, _ = DailyMealPlan.objects.get_or_create(
            weekly_plan=weekly_plan,
            date=date
        )
        daily_plans[date] = daily_plan
    
    context = {
        'weekly_plan': weekly_plan,
        'daily_plans': daily_plans,
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
    try:
        weekly_plan = WeeklyMealPlan.objects.get(id=weekly_plan_id, user=request.user)
        
        # Get all recipes from the weekly plan
        all_recipes = []
        for daily_plan in weekly_plan.daily_plans.all():
            all_recipes.extend(daily_plan.get_meals())

        # Aggregate ingredients
        ingredients = {}
        for recipe in all_recipes:
            if recipe and recipe.ingredients:  # Check if recipe exists and has ingredients
                for ingredient, details in recipe.ingredients.items():  # Access directly as dict
                    if ingredient in ingredients:
                        # Try to combine quantities if units match
                        if ingredients[ingredient]['unit'] == details['unit']:
                            ingredients[ingredient]['quantity'] += float(details['quantity'])
                    else:
                        ingredients[ingredient] = {
                            'quantity': float(details['quantity']),
                            'unit': details['unit']
                        }

        context = {
            'weekly_plan': weekly_plan,
            'ingredients': ingredients,
        }
        
        return render(request, 'recipes/shopping_list.html', context)
        
    except WeeklyMealPlan.DoesNotExist:
        messages.error(request, 'Weekly meal plan not found.')
        return redirect('recipes:meal_planner')

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

def subscription_page(request):
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'monthly_price_id': settings.STRIPE_MONTHLY_PLAN_ID,
        'yearly_price_id': settings.STRIPE_YEARLY_PLAN_ID
    }
    print("Context:", context)  # Debug print
    return render(request, 'recipes/subscription.html', context)

@login_required
def create_checkout_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        price_id = data.get('plan_id')
        print(f"Creating checkout session for price_id: {price_id}")  # Debug print

        checkout_session = stripe.checkout.Session.create(
            client_reference_id=str(request.user.id),  # Important for webhook
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/profile/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/profile/'),
        )
        print(f"Checkout session created: {checkout_session.id}")  # Debug print
        
        return JsonResponse({'url': checkout_session.url})
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=400)



@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    print("Webhook received!")  # Debug print

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print(f"Event type: {event.type}")  # Debug print
        
        if event.type == 'checkout.session.completed':
            session = event.data.object
            print(f"Processing checkout session: {session.id}")  # Debug print
            handle_successful_subscription(session)
            return JsonResponse({'status': 'subscription updated'})
            
    except Exception as e:
        print(f"Webhook error: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'status': 'unhandled event type'})

def handle_successful_subscription(session):
    try:
        user_id = session.client_reference_id
        user = User.objects.get(id=user_id)
        
        # Get the price ID from the session
        line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
        price_id = line_items.data[0].price.id if line_items.data else None

        # Determine the plan type
        plan_type = 'monthly' if price_id == settings.STRIPE_MONTHLY_PRICE_ID else 'yearly'
        valid_until = timezone.now() + timedelta(days=365 if plan_type == 'yearly' else 30)

        # Update or create subscription
        subscription, _ = Subscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan_type,
                'stripe_subscription_id': session.subscription,
                'valid_until': valid_until,
                'is_active': True
            }
        )
        
        print(f"Updated subscription for user {user.username} to {plan_type} plan")
        
    except Exception as e:
        print(f"Error in handle_successful_subscription: {str(e)}")
        raise

def subscription_success(request):
    return render(request, 'recipes/subscription_success.html')

@login_required
def check_premium_status(request):
    return JsonResponse({
        'is_premium': request.user.userprofile.is_premium,
        'username': request.user.username
    })

@login_required
def subscription_management(request):
    return render(request, 'recipes/subscription_management.html')

@login_required
def rate_recipe(request, recipe_id):
    """Handle recipe rating submission"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        try:
            value = int(request.POST.get('value', 0))
            if 1 <= value <= 5:
                Rating.objects.update_or_create(
                    recipe=recipe,
                    user=request.user,
                    defaults={'value': value}
                )
                messages.success(request, 'Rating added successfully!')
            else:
                messages.error(request, 'Rating must be between 1 and 5')
        except ValueError:
            messages.error(request, 'Invalid rating value')
    return redirect('recipes:recipe_detail', pk=recipe_id)

@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    if request.method == 'POST':
        text = request.POST.get('comment', '').strip()
        
        if text:
            Comment.objects.create(
                recipe=recipe,
                user=request.user,
                text=text
            )
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    
    return redirect('recipes:recipe_detail', recipe_id=recipe_id)

@login_required
def create_subscription(request):
    """Handle subscription creation"""
    if request.method == 'POST':
        if not request.user.userprofile.stripe_subscription_id:
            return JsonResponse({'error': 'No subscription ID found'}, status=400)
            
        request.user.userprofile.is_premium = True
        request.user.userprofile.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        else:
            messages.success(request, 'Successfully subscribed to premium plan!')
            return redirect('recipes:profile')
    return redirect('recipes:subscription')

@login_required
def cancel_subscription(request):
    print("Cancel subscription view called")  # Debug print
    if request.method != 'POST':
        print("Not a POST request")  # Debug print
        return redirect('recipes:profile')
        
    try:
        print(f"User: {request.user.username}")  # Debug print
        # Get the user's subscription
        subscription = Subscription.objects.get(user=request.user)
        print(f"Subscription found: {subscription.stripe_subscription_id}")  # Debug print
        
        # Check if user has an active subscription
        if not subscription.stripe_subscription_id:
            messages.warning(request, 'No active subscription found.')
            return redirect('recipes:profile')

        # Set up Stripe with your secret key
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print(f"Stripe API Key set: {stripe.api_key[:5]}...")  # Debug print (first 5 chars only)

        try:
            # Retrieve and cancel the subscription
            stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            print(f"Stripe subscription retrieved: {stripe_subscription.status}")  # Debug print
            
            if stripe_subscription and stripe_subscription.status != 'canceled':
                # Cancel at period end
                stripe_subscription.cancel_at_period_end = True
                stripe_subscription.save()

                # Update the subscription
                subscription.valid_until = timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
                subscription.is_active = False
                subscription.save()

                # Update user profile
                user_profile = request.user.userprofile
                user_profile.is_premium = False
                user_profile.subscription_cancelled = True
                user_profile.subscription_end_date = timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
                user_profile.save()

                messages.success(request, 'Your subscription has been cancelled. You will have access until the end of your current billing period.')
            else:
                messages.warning(request, 'Subscription already cancelled or inactive.')
        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")  # Debug print
            messages.error(request, f'Stripe error: {str(e)}')
        
    except Subscription.DoesNotExist:
        print("Subscription not found")  # Debug print
        messages.error(request, 'No subscription found.')
    except Exception as e:
        print(f"General error: {str(e)}")  # Debug print
        messages.error(request, f'Error cancelling subscription: {str(e)}')
    
    return redirect('recipes:profile')

@login_required
def premium_feature(request):
    if not request.user.userprofile.is_premium:
        return redirect('recipes:subscription')
    return render(request, 'recipes/premium_feature.html')

def upgrade_subscription(request):
    return render(request, 'recipes/upgrade_subscription.html')

def recipe_action(request, recipe_id, action):
    """Handle recipe actions with proper feedback"""
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        
        if action == 'favorite':
            if request.user.favorites.filter(id=recipe_id).exists():
                request.user.favorites.remove(recipe)
                message = 'Recipe removed from favorites'
            else:
                request.user.favorites.add(recipe)
                message = 'Recipe added to favorites'
                
        messages.success(request, message)
        return JsonResponse({'status': 'success', 'message': message})
        
    except Recipe.DoesNotExist:
        messages.error(request, 'Recipe not found')
        return JsonResponse({'status': 'error', 'message': 'Recipe not found'})
    except Exception as e:
        messages.error(request, 'An error occurred')
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def my_recipes(request):
    """Display user's own recipes"""
    recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'recipes/my_recipes.html', {'recipes': recipes})

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe', 'recipe__author')
    return render(request, 'recipes/favorites.html', {'favorites': favorites})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('recipes:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'recipes/login.html')

@login_required
def subscribe(request):
    plan_type = request.GET.get('plan')
    # Add your subscription logic here
    messages.success(request, f'Successfully subscribed to the {plan_type} plan!')
    return redirect('recipes:profile')

@login_required
def subscribe_plan(request):
    plan_type = request.GET.get('plan')
    if plan_type in ['monthly', 'annual']:
        # Here you would typically integrate with a payment processor
        # For now, we'll just show a success message
        messages.success(request, f'Successfully subscribed to the {plan_type} plan!')
    else:
        messages.error(request, 'Invalid subscription plan selected.')
    return redirect('recipes:profile')



@login_required
def search_recipes(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )[:10]  # Limit to 10 results
    
    return JsonResponse([{
        'id': recipe.id,
        'title': recipe.title,
        'cooking_time': recipe.cooking_time
    } for recipe in recipes], safe=False)

@login_required
@require_POST
def add_meal(request):
    data = json.loads(request.body)
    try:
        daily_plan = DailyMealPlan.objects.get(
            id=data['plan_id'],
            weekly_plan__user=request.user
        )
        recipe = Recipe.objects.get(id=data['recipe_id'])
        
        # Update the appropriate meal
        setattr(daily_plan, data['meal_type'], recipe)
        daily_plan.save()
        
        return JsonResponse({
            'success': True,
            'recipe': {
                'title': recipe.title,
                'cooking_time': recipe.cooking_time
            }
        })
    except (DailyMealPlan.DoesNotExist, Recipe.DoesNotExist):
        return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def remove_meal(request):
    data = json.loads(request.body)
    try:
        daily_plan = DailyMealPlan.objects.get(
            id=data['plan_id'],
            weekly_plan__user=request.user
        )
        
        # Remove the meal
        setattr(daily_plan, data['meal_type'], None)
        daily_plan.save()
        
        return JsonResponse({
            'success': True,
            'date': daily_plan.date.strftime('%Y-%m-%d')
        })
    except DailyMealPlan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Plan not found'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



