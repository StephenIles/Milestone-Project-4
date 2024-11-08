from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import json

# Create your models here.

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
