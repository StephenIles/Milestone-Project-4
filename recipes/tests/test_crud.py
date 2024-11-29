from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Recipe, Tag
import json
from django.urls import reverse

class CRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.recipe_data = {
            'title': 'Test Recipe',
            'description': 'Test description',
            'instructions': 'Test instructions',
            'cooking_time': 30,
            'ingredients': json.dumps({
                "flour": {"quantity": 500, "unit": "g"}
            }),
            'servings': 4
        }

    def test_recipe_list(self):
        """Test viewing the recipe list"""
        response = self.client.get('/recipes/')
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail(self):
        """Test viewing a recipe's details"""
        recipe = Recipe.objects.create(author=self.user, **self.recipe_data)
        response = self.client.get(f'/recipe/{recipe.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    def test_create_recipe(self):
        """Test creating a new recipe"""
        response = self.client.post('/recipe/new/', self.recipe_data)
        self.assertEqual(Recipe.objects.count(), 1)
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.title, 'Test Recipe')

    def test_update_recipe(self):
        """Test updating an existing recipe"""
        recipe = Recipe.objects.create(author=self.user, **self.recipe_data)
        updated_data = self.recipe_data.copy()
        updated_data['title'] = 'Updated Recipe Title'
        
        response = self.client.post(f'/recipe/{recipe.id}/edit/', updated_data)
        self.assertEqual(response.status_code, 302)  # Expecting redirect after successful update
        
        updated_recipe = Recipe.objects.get(id=recipe.id)
        self.assertEqual(updated_recipe.title, 'Updated Recipe Title')

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = Recipe.objects.create(author=self.user, **self.recipe_data)
        response = self.client.post(f'/recipe/{recipe.id}/delete/')
        self.assertEqual(Recipe.objects.count(), 0)

    def test_unauthorized_update(self):
        """Test that users cannot update other users' recipes"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        recipe = Recipe.objects.create(author=other_user, **self.recipe_data)
        updated_data = self.recipe_data.copy()
        updated_data['title'] = 'Updated Recipe Title'
        response = self.client.post(f'/recipe/{recipe.id}/edit/', updated_data)
        self.assertEqual(response.status_code, 404)

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON in recipe creation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('recipes:recipe_create'), {
            'title': 'Test Recipe',
            'description': 'Test description',
            'ingredients': '{invalid json}',
            'instructions': 'Test',
            'cooking_time': 30,
            'servings': 4
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('Invalid JSON format', form.errors['ingredients'])