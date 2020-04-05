from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_API = reverse('users:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTests(TestCase):
    """Test the users api (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        """Test creating user with valid payload is successful)"""
        payload = {
            'email': 'test@pokemail.net',
            'password': 'testpass283',
            'name': 'johnwick'
        }
        res = self.client.post(CREATE_USER_API, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test crearting user that already exists"""
        payload = {'email': 'test@pokemail.net', 'password': 'test234'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_API, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {'email': 'test@pokemail.net', 'password': 'pk'}
        res = self.client.post(CREATE_USER_API, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_avail = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_avail)
