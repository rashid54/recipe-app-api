from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTests(TestCase):
    """Test the publicly available api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieveing tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTAGApiTests(TestCase):
    """Test the privately available api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@pokemail.net',
            password='pass3'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test successful retrieval of tags of logged in user"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='desert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='test2@pokemail.net',
            password='pass5'
        )
        Tag.objects.create(user=user2, name='comfort food')
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='desert')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['name'], 'vegan')
        self.assertEqual(res.data[1]['name'], 'desert')

    def test_create_tags(self):
        """test creating tags"""
        payload = {'name': 'test tag'}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Tag.objects.all().filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_crete_tag_invalid(self):
        """test creating tag with invalid data"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned(self):
        """test retrieving tags assigned to recipes only"""
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')

        recipe = Recipe.objects.create(
            user=self.user,
            title='test recipe',
            time_minutes=3,
            price=34.82
        )
        recipe.tags.add(tag1)

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        res = self.client.get(
            TAGS_URL,
            {'assigned_only': 1}
        )

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
