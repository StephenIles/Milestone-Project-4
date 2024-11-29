from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.all_recipes, name='all_recipes'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('favorites/', views.favorites, name='favorites'),
    path('subscription/', views.subscription_page, name='subscription'),
    path('search/', views.recipe_search, name='recipe_search'),
    path('recipe/create/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipe/<int:recipe_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recipe/<int:recipe_id>/comment/', views.add_comment, name='add_comment'),
    path('profile/', views.profile, name='profile'),
    path('profile/subscribe/', views.subscribe_plan, name='subscribe'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('meal-planner/', views.meal_planner, name='meal_planner'),
    path('meal-planner/shopping-list/<int:weekly_plan_id>/', views.shopping_list, name='shopping_list'),
    path('api/recipes/search/', views.search_recipes, name='search_recipes'),
    path('api/meal-planner/add-meal/', views.add_meal, name='add_meal'),
    path('api/meal-planner/remove-meal/', views.remove_meal, name='remove_meal'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='recipes/password_reset.html',
            email_template_name='recipes/password_reset_email.html',
            subject_template_name='recipes/password_reset_subject.txt',
            success_url='/password-reset/done/'
        ),
        name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='recipes/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='recipes/password_reset_confirm.html',
            success_url='/password-reset-complete/'
        ),
        name='password_reset_confirm'),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='recipes/password_reset_complete.html'
        ),
        name='password_reset_complete'),
]
