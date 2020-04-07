from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """creates a sample recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 9,
        'price': 5.90
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test api available to public """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to access recipe api"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test api for logged in users"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@pokemail.net',
            password='pass3'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_successful(self):
        """Test retrieving recipes by logged in user"""
        sample_recipe(self.user)
        sample_recipe(self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_limited_to_user(self):
        """Test retrieving recipes for the user"""
        user2 = get_user_model().objects.create_user(
            email='test2@pokemail.net',
            password='pass2'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)
