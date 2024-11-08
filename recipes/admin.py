from django.contrib import admin
from .models import Recipe

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

# Register your models here.
