from django.test import TestCase
from django.contrib.auth.models import User
from ..forms import RecipeForm, RecipeSearchForm
import json

class RecipeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_valid_recipe_form(self):
        ingredients_json = {
            "flour": {"quantity": 500, "unit": "g"},
            "sugar": {"quantity": 200, "unit": "g"},
            "eggs": {"quantity": 2, "unit": "pieces"}
        }

        form_data = {
            'title': 'Test Recipe',
            'description': 'A test recipe description',
            'instructions': 'Test instructions',
            'cooking_time': 30,
            'ingredients': json.dumps(ingredients_json),
            'servings': 4
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_invalid_recipe_form(self):
        # Test with empty title
        ingredients_json = {
            "flour": {"quantity": 500, "unit": "g"}
        }
        
        form_data = {
            'title': '',
            'description': 'A test recipe description',
            'instructions': 'Test instructions',
            'cooking_time': 30,
            'ingredients': json.dumps(ingredients_json),
            'servings': 4
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_cooking_time_validation(self):
        """Test cooking time validation"""
        ingredients_json = {
            "flour": {"quantity": 500, "unit": "g"}
        }
        form_data = {
            'title': 'Test Recipe',
            'description': 'A test recipe description',
            'instructions': 'Test instructions',
            'cooking_time': -30,  # Invalid cooking time
            'ingredients': json.dumps(ingredients_json),
            'servings': 4
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cooking_time', form.errors)

    def test_servings_validation(self):
        """Test servings validation"""
        ingredients_json = {
            "flour": {"quantity": 500, "unit": "g"}
        }
        form_data = {
            'title': 'Test Recipe',
            'description': 'A test recipe description',
            'instructions': 'Test instructions',
            'cooking_time': 30,
            'ingredients': json.dumps(ingredients_json),
            'servings': 0  # Invalid servings
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('servings', form.errors)

class RecipeSearchFormTest(TestCase):
    def test_search_form_validation(self):
        # Test empty search
        form = RecipeSearchForm(data={'query': ''})
        self.assertTrue(form.is_valid())

        # Test with search query
        form = RecipeSearchForm(data={'query': 'cake'})
        self.assertTrue(form.is_valid())