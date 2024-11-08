from django.shortcuts import render

def home(request):
    return render(request, 'recipes/home.html')

def recipe_list(request):
    return render(request, 'recipes/recipe_list.html')
