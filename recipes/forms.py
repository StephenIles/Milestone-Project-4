from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'cooking_time', 'servings', 'image']
        widgets = {
            'ingredients': forms.Textarea(attrs={
                'placeholder': '{"ingredient": {"quantity": number, "unit": "string"}}',
                'rows': 4
            }),
            'instructions': forms.Textarea(attrs={'rows': 5}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients')
        try:
            # Check if it's already a dictionary
            if isinstance(ingredients, dict):
                return ingredients
            # If it's a string, try to parse it as JSON
            import json
            return json.loads(ingredients)
        except Exception as e:
            raise forms.ValidationError(
                "Please enter ingredients in valid JSON format. Example: "
                '{"flour": {"quantity": 500, "unit": "g"}}'
            )