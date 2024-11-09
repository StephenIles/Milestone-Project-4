from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Rating, Comment

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

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts about this recipe...'})
        }