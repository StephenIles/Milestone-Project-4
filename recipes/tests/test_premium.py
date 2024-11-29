from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import UserProfile, Collection, Recipe

class PremiumFeaturesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.premium_user = User.objects.create_user(
            username='premiumuser',
            password='testpass123'
        )
        self.premium_user.userprofile.is_premium = True
        self.premium_user.userprofile.save()

    def test_collection_limits(self):
        """Test collection creation limits for free vs premium users"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create collections up to the limit
        for i in range(Collection.MAX_FREE_COLLECTIONS):
            response = self.client.post('/collections/new/', {
                'name': f'Collection {i}',
                'description': 'Test description',
                'is_public': True
            })
            self.assertEqual(response.status_code, 302)  # Success

        # Try to create one more collection (should fail)
        response = self.client.post('/collections/new/', {
            'name': 'One Too Many',
            'description': 'Test description',
            'is_public': True
        })
        self.assertEqual(response.status_code, 302)  # Redirects to error page or collection list
        
        # Check for error message (adjust the message level and text to match your implementation)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            message.level == 40 and  # ERROR level
            'collection limit' in str(message).lower()
            for message in messages
        ))

        # Test premium user
        self.client.login(username='premiumuser', password='testpass123')
        for i in range(Collection.MAX_FREE_COLLECTIONS + 2):
            response = self.client.post('/collections/new/', {
                'name': f'Premium Collection {i}',
                'description': 'Test description',
                'is_public': True
            })
            self.assertEqual(response.status_code, 302)  # All should succeed 