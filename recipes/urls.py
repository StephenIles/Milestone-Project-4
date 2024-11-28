from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.recipe_list, name='recipes'),
    path('accounts/profile/', views.profile, name='profile'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('recipes/favorite/<int:recipe_id>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_recipes, name='favorite_list'),
    path('tags/', views.tag_list, name='tag_list'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('search/', views.recipe_search, name='recipe_search'),
] 