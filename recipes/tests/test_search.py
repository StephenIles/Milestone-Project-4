from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Recipe, Category
import json

class SearchTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Chocolate Cake',
            author=self.user,
            description='Delicious chocolate cake',
            instructions='Bake it',
            cooking_time=30,
            ingredients=json.dumps({"chocolate": {"quantity": 200, "unit": "g"}}),
            servings=4
        )

    def test_search_by_title(self):
        """Test searching for recipes by title"""
        response = self.client.get('/?q=chocolate')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chocolate Cake')

    def test_filter_by_cooking_time(self):
        """Test filtering recipes by cooking time"""
        response = self.client.get('/?cooking_time=30')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chocolate Cake')

    def test_search_by_ingredient(self):
        """Test searching recipes by ingredient"""
        response = self.client.get('/?ingredient=chocolate')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chocolate Cake')

    def test_search_by_cooking_time_range(self):
        """Test searching recipes by cooking time range"""
        response = self.client.get('/?max_time=45')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chocolate Cake')

    def test_search_by_category(self):
        """Test searching recipes by category"""
        category = Category.objects.create(name='Desserts')
        self.recipe.category = category
        self.recipe.save()
        response = self.client.get(f'/?category={category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chocolate Cake')
  