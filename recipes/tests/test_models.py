from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Recipe, Category, Rating, Comment
from django.core.exceptions import ValidationError
import json
from decimal import Decimal

class RecipeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.recipe_data = {
            'title': 'Test Recipe',
            'author': self.user,
            'description': 'Test description',
            'instructions': 'Test instructions',
            'cooking_time': 30,
            'ingredients': json.dumps({
                "flour": {"quantity": 500, "unit": "g"}
            }),
            'servings': 4
        }
        self.recipe = Recipe.objects.create(**self.recipe_data)

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.title, 'Test Recipe')
        self.assertEqual(self.recipe.author, self.user)
        self.assertEqual(self.recipe.description, 'Test description')
        self.assertEqual(self.recipe.instructions, 'Test instructions')
        self.assertEqual(self.recipe.cooking_time, 30)
        self.assertEqual(self.recipe.servings, 4)

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), 'Test Recipe')

    def test_recipe_category_relationship(self):
        """Test recipe-category relationship"""
        category = Category.objects.create(name='Main Course')
        self.recipe.category = category
        self.recipe.save()
        self.assertEqual(self.recipe.category.name, 'Main Course')

    def test_recipe_author_deletion(self):
        """Test what happens to recipe when author is deleted"""
        user_id = self.user.id
        self.user.delete()
        # Check if recipe is deleted or handled appropriately
        with self.assertRaises(Recipe.DoesNotExist):
            Recipe.objects.get(author_id=user_id)

    def test_recipe_ingredients_validation(self):
        """Test ingredient format validation"""
        with self.assertRaises(ValidationError):
            invalid_recipe = Recipe(
                title='Invalid Recipe',
                author=self.user,
                description='Test description',
                ingredients=[1, 2, 3],  # Invalid format
                instructions='Test',
                cooking_time=30,
                servings=4
            )
            invalid_recipe.full_clean()

    def test_recipe_servings_validation(self):
        """Test servings validation"""
        with self.assertRaises(ValidationError):
            invalid_recipe = Recipe(
                title='Invalid Recipe',
                author=self.user,
                description='Test description',
                ingredients=json.dumps({
                    "flour": {"quantity": 500, "unit": "g"}
                }),
                instructions='Test',
                cooking_time=30,
                servings=-1  # Invalid servings
            )
            invalid_recipe.full_clean()

    def test_recipe_rating(self):
        """Test recipe rating functionality"""
        # Create a rating
        Rating.objects.create(recipe=self.recipe, user=self.user, value=5)
        
        # Create another rating with different user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        Rating.objects.create(recipe=self.recipe, user=other_user, value=3)
        
        # Test average calculation
        self.assertEqual(self.recipe.average_rating, 4.0)

    def test_recipe_comments(self):
        """Test recipe comments functionality"""
        comment = Comment.objects.create(
            recipe=self.recipe,
            user=self.user,
            text='Great recipe!'
        )
        self.assertEqual(comment.text, 'Great recipe!')
        self.assertEqual(comment.recipe, self.recipe)

class CategoryTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')