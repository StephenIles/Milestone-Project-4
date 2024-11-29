from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import UserProfile, Subscription
from unittest import skip

@skip("Subscription functionality not implemented")
class SubscriptionTest(TestCase):
    """Tests for subscription functionality - currently not implemented"""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_subscription_creation(self):
        self.skipTest("Subscription functionality not implemented")

    def test_subscription_cancellation(self):
        self.skipTest("Subscription functionality not implemented")
