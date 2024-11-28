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
    path('recipe/<int:recipe_id>/share/<str:platform>/', views.track_share, name='track_share'),
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/new/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:pk>/edit/', views.collection_edit, name='collection_edit'),
    path('collections/<int:pk>/delete/', views.collection_delete, name='collection_delete'),
    path('collections/<int:collection_pk>/add/<int:recipe_pk>/', views.collection_add_recipe, name='collection_add_recipe'),
    path('collections/<int:collection_pk>/remove/<int:recipe_pk>/', views.collection_remove_recipe, name='collection_remove_recipe'),
    path('api/collections/', views.get_user_collections, name='get_user_collections'),
] 