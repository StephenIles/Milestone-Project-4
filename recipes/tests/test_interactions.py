from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Recipe, Rating, Comment
import json

class RecipeInteractionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            description='Test description',
            instructions='Test instructions',
            cooking_time=30,
            ingredients=json.dumps({"flour": {"quantity": 500, "unit": "g"}}),
            servings=4
        )
        self.client.login(username='testuser', password='testpass123')

    def test_add_rating(self):
        """Test adding a rating to a recipe"""
        response = self.client.post(f'/recipe/{self.recipe.id}/rate/', {
            'value': 5
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.first().value, 5)

    def test_add_comment(self):
        """Test adding a comment to a recipe"""
        response = self.client.post(f'/recipe/{self.recipe.id}/comment/', {
            'text': 'Great recipe!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, 'Great recipe!')

    def test_average_rating(self):
        """Test calculation of average rating"""
        Rating.objects.create(recipe=self.recipe, user=self.user, value=5)
        other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )
        Rating.objects.create(recipe=self.recipe, user=other_user, value=3)
        self.assertEqual(self.recipe.average_rating, 4.0)
