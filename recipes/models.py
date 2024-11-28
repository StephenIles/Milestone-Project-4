from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_premium = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()

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

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']  # Prevent duplicate favorites
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def recipe_count(self):
        return self.recipes.count()
    
class ShareCount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='share_counts')
    platform = models.CharField(max_length=20)
    count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['recipe', 'platform']

class Collection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    recipes = models.ManyToManyField(Recipe, related_name='collections')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Free tier limitations
    MAX_FREE_COLLECTIONS = 3
    MAX_RECIPES_PER_COLLECTION = 10
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def recipe_count(self):
        return self.recipes.count()
    
    def can_add_recipe(self, user):
        if hasattr(user, 'profile') and user.profile.is_premium:
            return True
        return self.recipes.count() < self.MAX_RECIPES_PER_COLLECTION
    
    @classmethod
    def can_create_collection(cls, user):
        if hasattr(user, 'profile') and user.profile.is_premium:
            return True
        return user.collections.count() < cls.MAX_FREE_COLLECTIONS
    
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    date = models.DateField()
    breakfast = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name='breakfast_plans')
    lunch = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name='lunch_plans')
    dinner = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name='dinner_plans')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username}'s meal plan for {self.date}"

    @classmethod
    def can_create_plan(cls, user):
        return hasattr(user, 'profile') and user.profile.is_premium

    def get_shopping_list(self):
        """Generate a combined shopping list for all meals in the plan"""
        shopping_list = {}
        
        meals = [self.breakfast, self.lunch, self.dinner]
        for meal in meals:
            if meal:
                for ingredient, details in meal.ingredients.items():
                    if ingredient in shopping_list:
                        # Convert quantities to same unit if possible and add
                        current_qty = Decimal(str(shopping_list[ingredient]['quantity']))
                        add_qty = Decimal(str(details['quantity']))
                        if shopping_list[ingredient]['unit'] == details['unit']:
                            shopping_list[ingredient]['quantity'] = current_qty + add_qty
                    else:
                        shopping_list[ingredient] = {
                            'quantity': details['quantity'],
                            'unit': details['unit']
                        }
        
        return shopping_list

class WeeklyMealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_meal_plans')
    start_date = models.DateField()
    end_date = models.DateField()
    daily_plans = models.ManyToManyField(MealPlan, related_name='weekly_plan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.username}'s meal plan for week of {self.start_date}"

    def get_weekly_shopping_list(self):
        """Combine shopping lists from all daily plans"""
        weekly_list = {}
        
        for plan in self.daily_plans.all():
            daily_list = plan.get_shopping_list()
            for ingredient, details in daily_list.items():
                if ingredient in weekly_list:
                    current_qty = Decimal(str(weekly_list[ingredient]['quantity']))
                    add_qty = Decimal(str(details['quantity']))
                    if weekly_list[ingredient]['unit'] == details['unit']:
                        weekly_list[ingredient]['quantity'] = current_qty + add_qty
                else:
                    weekly_list[ingredient] = details.copy()
        
        return weekly_list

