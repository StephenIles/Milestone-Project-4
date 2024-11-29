from django.test import TestCase, Client
from django.contrib.auth.models import User
import json

class APITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_get_user_collections(self):
        """Test the collections API endpoint"""
        response = self.client.get('/api/collections/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('collections', data)
        self.assertIsInstance(data['collections'], list)

    def test_unauthorized_api_access(self):
        """Test API access without authentication"""
        self.client.logout()
        response = self.client.get('/api/collections/')
        self.assertEqual(response.status_code, 302)  # Redirect to login 