from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import json

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.JSONField(
        help_text="Format: {'ingredient_name': {'quantity': number, 'unit': string}}"
    )
    instructions = models.TextField()
    cooking_time = models.IntegerField(help_text="Cooking time in minutes")
    servings = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes'
    )

    def clean(self):
        # Validate ingredients format
        if self.ingredients:
            try:
                for ingredient, details in self.ingredients.items():
                    if not isinstance(details, dict):
                        raise ValidationError("Each ingredient must have quantity and unit details")
                    if 'quantity' not in details or 'unit' not in details:
                        raise ValidationError("Each ingredient must specify quantity and unit")
            except AttributeError:
                raise ValidationError("Ingredients must be a dictionary")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    def get_ingredients_list(self):
        """Returns a formatted list of ingredients"""
        return [
            f"{details['quantity']} {details['unit']} {name}"
            for name, details in self.ingredients.items()
        ]

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['recipe', 'user']  # One rating per user per recipe

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.value}"

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"
