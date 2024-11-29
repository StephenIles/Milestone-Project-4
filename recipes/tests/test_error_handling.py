from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class ErrorHandlingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_404_handling(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)

    def test_invalid_recipe_id(self):
        """Test handling of invalid recipe ID"""
        response = self.client.get('/recipe/999999/')
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
