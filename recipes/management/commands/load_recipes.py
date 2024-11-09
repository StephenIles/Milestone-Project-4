from django.core.management.base import BaseCommand
from recipes.models import Recipe
from django.contrib.auth.models import User
import json
import os

class Command(BaseCommand):
    help = 'Load sample recipes from JSON file'

    def handle(self, *args, **kwargs):
        # Get the first user or create one if none exists
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('admin', 'admin@example.com', 'admin')

        # Load the JSON file
        file_path = os.path.join('recipes', 'fixtures', 'sample_recipes.json')
        with open(file_path, 'r') as file:
            recipes_data = json.load(file)

        for recipe_data in recipes_data['recipes']:
            Recipe.objects.create(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                cooking_time=recipe_data['cooking_time'],
                servings=recipe_data['servings'],
                author=user
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created recipe "{recipe_data["title"]}"')
            ) 