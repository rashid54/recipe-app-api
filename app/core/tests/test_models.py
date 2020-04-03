from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'bullnight@pokemail.net'
        password = 'pass439'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email of new user is normalized or not"""
        email = 'bullnight@POKEMAIL.net'
        user = get_user_model().objects.create_user(email, 'pass439')

        self.assertEqual(user.email, email.lower())

    def test_email_uniqueness(self):
        """test the uniqueness of the email of user"""
        email = 'bullnight@pokemail.net'
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(email, 'pass439')
            get_user_model().objects.create_user(email, 'pass539')

    def test_new_user_invalid_email(self):
        """Test creating new user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'pass539')

    def test_create_new_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            'bullnight@pokemail.net',
            'pass539'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
