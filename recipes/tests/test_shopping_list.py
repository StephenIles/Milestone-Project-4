from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Recipe, MealPlan, WeeklyMealPlan
from decimal import Decimal
import json

class ShoppingListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create recipes with ingredients
        self.recipe1 = Recipe.objects.create(
            title='Recipe 1',
            author=self.user,
            description='Test description 1',
            ingredients=json.dumps({
                "flour": {"quantity": 500, "unit": "g"}
            }),
            instructions='Test',
            cooking_time=30,
            servings=4
        )
        self.recipe2 = Recipe.objects.create(
            title='Recipe 2',
            author=self.user,
            description='Test description 2',
            ingredients=json.dumps({
                "flour": {"quantity": 300, "unit": "g"}
            }),
            instructions='Test',
            cooking_time=30,
            servings=4
        )

    def test_shopping_list_generation(self):
        """Test shopping list combines ingredients correctly"""
        # Create a meal plan with both recipes
        meal_plan = MealPlan.objects.create(
            user=self.user,
            date='2024-03-01'
        )
        meal_plan.breakfast = self.recipe1
        meal_plan.dinner = self.recipe2
        meal_plan.save()
        
        # Get the shopping list
        shopping_list = meal_plan.get_shopping_list()
        
        # Test that flour quantities were combined correctly
        self.assertIn('flour', shopping_list)
        self.assertEqual(Decimal(str(shopping_list['flour']['quantity'])), Decimal('800'))
        self.assertEqual(shopping_list['flour']['unit'], 'g')

    def test_shopping_list_different_units(self):
        """Test shopping list with different units"""
        # Create recipes with different units
        recipe3 = Recipe.objects.create(
            title='Recipe 3',
            author=self.user,
            description='Test description 3',
            ingredients=json.dumps({
                "sugar": {"quantity": 1, "unit": "kg"}
            }),
            instructions='Test',
            cooking_time=30,
            servings=4
        )
        recipe4 = Recipe.objects.create(
            title='Recipe 4',
            author=self.user,
            description='Test description 4',
            ingredients=json.dumps({
                "sugar": {"quantity": 500, "unit": "g"}
            }),
            instructions='Test',
            cooking_time=30,
            servings=4
        )

        # Create meal plan with these recipes
        meal_plan = MealPlan.objects.create(
            user=self.user,
            date='2024-03-01',
            breakfast=recipe3,
            lunch=recipe4
        )

        shopping_list = meal_plan.get_shopping_list()
        
        # For now, ingredients with different units are kept separate
        # You might want to implement unit conversion in the future
        self.assertIn('sugar', shopping_list)