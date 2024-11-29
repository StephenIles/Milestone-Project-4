from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
from decimal import Decimal
from django.utils import timezone
from django.db.models import Avg

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    is_premium = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    subscription_cancelled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def subscription_active(self):
        """
        Returns True if the user has an active subscription or is within their paid period
        even if they've cancelled (until the end date).
        """
        if self.subscription_end_date:
            return self.subscription_end_date > timezone.now()
        return self.is_premium

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

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
            # Handle duplicate slugs
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Handle duplicate slugs
            original_slug = self.slug
            counter = 1
            while Tag.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_recipe_count(self):
        return self.recipes.count()

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
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes'
    )
    favorites = models.ManyToManyField(
        User,
        through='Favorite',
        related_name='favorite_recipes'
    )

    def clean(self):
        super().clean()
        errors = {}
        
        # Validate ingredients format
        if isinstance(self.ingredients, list):
            errors['ingredients'] = 'Ingredients must be a dictionary with quantity and unit details'
        elif isinstance(self.ingredients, dict):
            for ingredient, details in self.ingredients.items():
                if not isinstance(details, dict) or 'quantity' not in details or 'unit' not in details:
                    errors['ingredients'] = 'Each ingredient must have quantity and unit details'
        
        # Validate servings
        if self.servings is not None and self.servings <= 0:
            errors['servings'] = 'Servings must be a positive number'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    def get_formatted_ingredients(self):
        """Returns a formatted list of ingredients"""
        formatted_ingredients = []
        for ingredient, details in self.ingredients.items():
            quantity = details.get('quantity', '')
            unit = details.get('unit', '')
            formatted = f"{quantity} {unit} {ingredient}".strip()
            formatted_ingredients.append(formatted)
        return formatted_ingredients
    
    @property
    def average_rating(self):
        avg = self.ratings.aggregate(Avg('value'))['value__avg']
        return avg if avg is not None else 0.0

class Rating(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE,
        related_name='recipe_favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"

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
        """Check if user can create a new collection"""
        if hasattr(user, 'userprofile') and user.userprofile.subscription_active:
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
        """Combine ingredients from all meals in the plan"""
        shopping_list = {}
        meals = [self.breakfast, self.lunch, self.dinner]
        
        for meal in meals:
            if meal:
                # Parse the JSON string to dictionary
                meal_ingredients = json.loads(meal.ingredients)
                for ingredient, details in meal_ingredients.items():
                    if ingredient in shopping_list:
                        # Convert quantities to same unit if possible and add
                        current_qty = Decimal(str(shopping_list[ingredient]['quantity']))
                        add_qty = Decimal(str(details['quantity']))
                        if shopping_list[ingredient]['unit'] == details['unit']:
                            shopping_list[ingredient]['quantity'] = current_qty + add_qty
                    else:
                        shopping_list[ingredient] = details.copy()
        
        return shopping_list

class WeeklyMealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s meal plan - {self.start_date}"

class DailyMealPlan(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner')
    ]

    weekly_plan = models.ForeignKey(WeeklyMealPlan, related_name='daily_plans', on_delete=models.CASCADE)
    date = models.DateField()
    breakfast = models.ForeignKey('Recipe', related_name='breakfast_meals', on_delete=models.SET_NULL, null=True, blank=True)
    lunch = models.ForeignKey('Recipe', related_name='lunch_meals', on_delete=models.SET_NULL, null=True, blank=True)
    dinner = models.ForeignKey('Recipe', related_name='dinner_meals', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['date']
        unique_together = ['weekly_plan', 'date']

    def __str__(self):
        return f"Meal plan for {self.date}"

    def get_meals(self):
        """Return all non-null meals for this day"""
        meals = []
        if self.breakfast:
            meals.append(self.breakfast)
        if self.lunch:
            meals.append(self.lunch)
        if self.dinner:
            meals.append(self.dinner)
        return meals

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly Premium'),
        ('yearly', 'Yearly Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.plan} subscription"

    class Meta:
        db_table = 'user_subscription'


