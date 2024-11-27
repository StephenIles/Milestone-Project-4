from django.contrib import admin
from .models import Recipe, Category, Tag

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'cooking_time', 'servings')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'description')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['ingredients'].help_text = """
        Enter ingredients in JSON format, e.g.:
        {
            "flour": {"quantity": 500, "unit": "g"},
            "sugar": {"quantity": 200, "unit": "g"},
            "eggs": {"quantity": 2, "unit": "piece"}
        }
        """
        return form

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Number of Recipes'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Number of Recipes'

# Register your models here.
