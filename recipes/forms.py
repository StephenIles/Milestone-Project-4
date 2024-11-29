from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Rating, Comment, Tag, Category, Collection
from django.template.defaultfilters import slugify

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class RecipeForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'tag-input',
            'placeholder': 'Add tags (comma separated)'
        })
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 
                 'cooking_time', 'servings', 'image', 'category', 'tags']
        widgets = {
            'ingredients': forms.Textarea(attrs={
                'placeholder': '{"ingredient": {"quantity": number, "unit": "string"}}',
                'rows': 4
            }),
            'instructions': forms.Textarea(attrs={'rows': 5}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing recipe and it has tags attribute, populate tags field
        if self.instance.pk and hasattr(self.instance, 'tags'):
            self.initial['tags'] = ', '.join(tag.name for tag in self.instance.tags.all())

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

    def clean_tags(self):
        tag_string = self.cleaned_data.get('tags', '')
        if not tag_string:
            return []
        
        # Split tags and clean them
        tag_names = [t.strip().lower() for t in tag_string.split(',') if t.strip()]
        tags = []
        
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags.append(tag)
        
        return tags

    def clean_cooking_time(self):
        cooking_time = self.cleaned_data.get('cooking_time')
        if cooking_time is not None and cooking_time <= 0:
            raise forms.ValidationError("Cooking time must be greater than 0")
        return cooking_time

    def clean_servings(self):
        servings = self.cleaned_data.get('servings')
        if servings is not None and servings <= 0:
            raise forms.ValidationError("Number of servings must be greater than 0")
        return servings

    def save(self, commit=True):
        recipe = super().save(commit=False)
        if commit:
            recipe.save()
            # Handle tags
            self.save_tags(recipe)
        return recipe

    def save_tags(self, recipe):
        tags = self.cleaned_data.get('tags', [])
        recipe.tags.clear()  # Remove existing tags
        recipe.tags.add(*tags)  # Add new tags

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

class RecipeSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Search recipes...'
        })
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        empty_label="All Categories"
    )
    tags = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    cooking_time = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Any Time'),
            ('15', 'Under 15 minutes'),
            ('30', 'Under 30 minutes'),
            ('60', 'Under 1 hour'),
            ('120', 'Under 2 hours'),
        ]
    )
    rating = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Any Rating'),
            ('4', '4+ Stars'),
            ('3', '3+ Stars'),
            ('2', '2+ Stars'),
        ]
    )

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }