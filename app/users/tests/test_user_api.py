from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_API = reverse('users:create')
TOKEN_URL = reverse('users:token')
ME_URL = reverse('users:me')


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

    def test_create_token_for_user(self):
        """Test token creation with valid payload"""
        payload = {'email': 'test@pokemail.net', 'password': 'right'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertContains(res, 'token', status_code=status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test token is not created if credentials are invalid"""
        create_user(email='test@pokemail.net', password='right')
        res = self.client.post(TOKEN_URL, {
                                            'email': 'test@pokemail.net',
                                            'password': 'wrong'
                                          })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test token not created without existing user"""
        res = self.client.post(TOKEN_URL, {
                                            'email': 'test@pokemail.net',
                                            'password': 'testpass'
                                          })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_password(self):
        """Test token not created without password"""
        res = self.client.post(TOKEN_URL, {
                                            'email': 'test@pokemail.net',
                                            'password': ''
                                          })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test unauthorized user accessing user info"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test api endpoints that require authentication"""

    def setUp(self):
        """setting up the client"""
        self.user = create_user(
            email='test@pokemail.net',
            name='testname',
            password='pass3'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test post not allowed on me url"""
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile"""
        payload = {
            'email': 'newemail@pokemail.net',
            'name': 'new name',
            'password': 'newpass'
        }
        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload['email'])
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
