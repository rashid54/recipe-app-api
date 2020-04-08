import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def image_url(recipe_id):
    """Returns url for uploading recipe image"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Returns url for a recipe's details"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='cold drink'):
    """returns a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='water'):
    """returns a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """creates a sample recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 9,
        'price': 5.90
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    recipe.tags.add(sample_tag(user=user))
    recipe.ingredient.add(sample_ingredient(user=user))
    return recipe


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

    def test_view_recipe_detail(self):
        """Test viewing a recipe details"""
        recipe = sample_recipe(user=self.user)
        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'basic recipe1',
            'time_minutes': 4,
            'price': 9.27
        }
        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            value = getattr(recipe, key)
            if isinstance(value, Decimal):
                value = float(value)
            self.assertEqual(payload[key], value)

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='sosha')
        tag2 = sample_tag(user=self.user, name='suger')
        payload = {
            'title': 'recipe with tags',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 23.89
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='sha')
        ingredient2 = sample_ingredient(user=self.user, name='fesuger')
        payload = {
            'title': 'recipe with tags',
            'ingredient': [ingredient1.id, ingredient2.id],
            'time_minutes': 60,
            'price': 23.89
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredient = recipe.ingredient.all()
        self.assertEqual(ingredient.count(), 2)
        self.assertIn(ingredient1, ingredient)
        self.assertIn(ingredient2, ingredient)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='curry')

        payload = {'title': 'chicken soup', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertIn(new_tag, tags)
        self.assertEqual(len(tags), 1)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'recipe with tags',
            'time_minutes': 60,
            'price': 23.89
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(float(recipe.price), payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@pokemail.net',
            'pass3'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.client)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading image to recipe"""
        url = image_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (100,100))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image_to_recipe(self):
        """Test uploading invalid image to recipe"""
        url = image_url(self.recipe.id)
        res = self.client.post(url, {'image': 'fake image'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
