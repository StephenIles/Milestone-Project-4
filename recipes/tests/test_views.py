from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from recipes.models import (
    Recipe, Category, Tag, Rating, Comment, Collection, 
    UserProfile, MealPlan, WeeklyMealPlan, ShareCount
)
from datetime import date, timedelta
import json

class BaseViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123',
            email='test@example.com'
        )
        
        # Create category and tag
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.tag = Tag.objects.create(name='Test Tag')
        
        # Create test recipe with proper JSON format
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            author=self.user,
            cooking_time=30,
            servings=4,
            ingredients={
                'ingredient 1': {'quantity': 1, 'unit': 'cup'},
                'ingredient 2': {'quantity': 2, 'unit': 'tbsp'}
            },
            instructions='Test instructions',
            category=self.category
        )
        self.recipe.tags.add(self.tag)
        
        # Create test collection
        self.collection = Collection.objects.create(
            name='Test Collection',
            owner=self.user,
            description='Test Description'
        )
        
        # Create test meal plan
        self.meal_plan = MealPlan.objects.create(
            user=self.user,
            date=date.today(),
            breakfast=self.recipe
        )
        
        self.client = Client()

class RecipeViewTests(BaseViewTest):
    def test_recipe_list(self):
        response = self.client.get(reverse('recipes:recipes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_detail(self):
        response = self.client.get(
            reverse('recipes:recipe_detail', kwargs={'pk': self.recipe.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_create(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'New Recipe',
            'description': 'New Description',
            'cooking_time': 30,
            'servings': 4,
            'ingredients': json.dumps({
                'new ingredient': {'quantity': 1, 'unit': 'cup'}
            }),
            'instructions': 'New instructions',
            'category': self.category.id
        }
        response = self.client.post(reverse('recipes:recipe_create'), data)
        self.assertEqual(response.status_code, 302)

    def test_recipe_list_with_filters(self):
        """Test recipe list with query parameters"""
        response = self.client.get(reverse('recipes:recipes') + '?q=Test&cooking_time=30&servings=4')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_edit(self):
        """Test recipe editing"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'Updated Recipe',
            'description': 'Updated Description',
            'cooking_time': 45,
            'servings': 6,
            'ingredients': json.dumps({
                'updated ingredient': {'quantity': 2, 'unit': 'cups'}
            }),
            'instructions': 'Updated instructions',
            'category': self.category.id
        }
        response = self.client.post(
            reverse('recipes:recipe_edit', kwargs={'pk': self.recipe.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)
        updated_recipe = Recipe.objects.get(pk=self.recipe.pk)
        self.assertEqual(updated_recipe.title, 'Updated Recipe')

    def test_recipe_delete(self):
        """Test recipe deletion"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('recipes:recipe_delete', kwargs={'pk': self.recipe.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())

class InteractionTests(BaseViewTest):
    def test_recipe_rating(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('recipes:rate_recipe', kwargs={'recipe_id': self.recipe.pk}),
            {'value': 4}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rating.objects.first().value, 4)

    def test_recipe_comment(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('recipes:add_comment', kwargs={'recipe_id': self.recipe.pk}),
            {'text': 'Great recipe!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.first().text, 'Great recipe!')

class CollectionTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        # Make user premium by setting the correct fields
        self.user.userprofile.is_premium = True
        self.user.userprofile.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
        self.user.userprofile.save()

    def test_collection_create(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('recipes:collection_create'),
            {
                'name': 'New Collection',
                'description': 'New Description',
                'is_public': True
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_collection_add_recipe(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('recipes:collection_add_recipe', kwargs={
                'collection_pk': self.collection.pk,
                'recipe_pk': self.recipe.pk
            }),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.collection.recipes.filter(pk=self.recipe.pk).exists())

class MealPlannerTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.user.userprofile.is_premium = True
        self.user.userprofile.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
        self.user.userprofile.save()
        MealPlan.objects.filter(user=self.user, date=date.today()).delete()

    def test_update_meal(self):
        self.client.login(username='testuser', password='testpass123')
        
        tomorrow = date.today() + timedelta(days=1)
        meal_plan = MealPlan.objects.create(
            user=self.user,
            date=tomorrow
        )

        # Create JSON payload
        data = json.dumps({
            'meal_type': 'lunch',
            'recipe_id': self.recipe.pk
        })

        response = self.client.post(
            reverse('recipes:update_meal', kwargs={'plan_id': meal_plan.pk}),
            data,
            content_type='application/json',  # Set content type to JSON
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        if response.status_code not in [200, 302]:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content}")
            print(f"Request data: {data}")
        
        self.assertIn(response.status_code, [200, 302])
        
        meal_plan.refresh_from_db()
        self.assertEqual(meal_plan.lunch, self.recipe)

    def test_meal_planner_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:meal_planner'), follow=True)
        self.assertEqual(response.status_code, 200)

class SearchAndFilterTests(BaseViewTest):
    def test_recipe_search_with_filters(self):
        """Test recipe search with various filters"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add a rating to test rating filter
        Rating.objects.create(user=self.user, recipe=self.recipe, value=4)
        
        url = reverse('recipes:recipe_search')
        response = self.client.get(f"{url}?q=Test&category={self.category.id}&cooking_time=30&rating=4")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    def test_category_list(self):
        """Test category listing"""
        response = self.client.get(reverse('recipes:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/category_list.html')
        self.assertContains(response, 'Test Category')

    def test_tag_list_and_detail(self):
        """Test tag listing view"""
        # Create a recipe with the tag
        recipe = Recipe.objects.create(
            title='Tagged Recipe',
            description='Test Description',
            author=self.user,
            cooking_time=30,
            servings=4,
            ingredients={
                'ingredient 1': {'quantity': 1, 'unit': 'cup'}
            },
            instructions='Test instructions',
            category=self.category
        )
        
        # Ensure tag has a slug and only one recipe
        self.tag.slug = 'test-tag'
        self.tag.save()
        
        # Remove any existing recipes from the tag and add only our test recipe
        self.tag.recipes.clear()
        recipe.tags.add(self.tag)
        
        # Test tag list
        response = self.client.get(reverse('recipes:tag_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/tag_list.html')
        self.assertContains(response, self.tag.name)
        
        # Get the actual count and check for that
        expected_count = f"{self.tag.get_recipe_count()} recipes"
        self.assertContains(response, expected_count)

    def test_category_detail(self):
        """Test category detail view"""
        response = self.client.get(
            reverse('recipes:category_detail', kwargs={'pk': self.category.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')

class SocialSharingTests(BaseViewTest):
    def test_track_share(self):
        """Test social sharing tracking"""
        response = self.client.post(
            reverse('recipes:track_share', kwargs={
                'recipe_id': self.recipe.pk,
                'platform': 'facebook'
            })
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 1)

    def test_track_share_invalid_method(self):
        """Test social sharing with GET method"""
        response = self.client.get(
            reverse('recipes:track_share', kwargs={
                'recipe_id': self.recipe.pk,
                'platform': 'facebook'
            })
        )
        self.assertEqual(response.status_code, 400)

class SubscriptionTests(BaseViewTest):
    def test_subscription_page(self):
        """Test subscription page load"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:subscription'))
        self.assertEqual(response.status_code, 200)

    def test_check_premium_status(self):
        """Test premium status check"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:check_premium_status'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['is_premium'])

    def test_subscription_management(self):
        """Test subscription management page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:subscription_management'))
        self.assertEqual(response.status_code, 200)

    def test_cancel_subscription_no_active_subscription(self):
        """Test cancelling non-existent subscription"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('recipes:cancel_subscription'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'No active subscription found')

    def test_subscription_success(self):
        """Test subscription success page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:subscription_success'))
        self.assertEqual(response.status_code, 200)

    def test_create_subscription(self):
        """Test subscription creation"""
        self.client.login(username='testuser', password='testpass123')
        # Set up the stripe subscription ID first
        self.user.userprofile.stripe_subscription_id = 'test_sub_123'
        self.user.userprofile.save()
        
        response = self.client.post(
            reverse('recipes:create_subscription'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Refresh user profile from database
        self.user.userprofile.refresh_from_db()
        self.assertTrue(self.user.userprofile.is_premium)

class CollectionAPITests(BaseViewTest):
    def test_get_user_collections(self):
        """Test API endpoint for user collections"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:get_user_collections'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['collections']), 1)
        self.assertEqual(data['collections'][0]['name'], 'Test Collection')

    def test_collection_remove_recipe(self):
        """Test removing recipe from collection"""
        self.client.login(username='testuser', password='testpass123')
        # First add a recipe
        self.collection.recipes.add(self.recipe)
        
        response = self.client.post(
            reverse('recipes:collection_remove_recipe', kwargs={
                'collection_pk': self.collection.pk,
                'recipe_pk': self.recipe.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.collection.recipes.filter(pk=self.recipe.pk).exists())
