from core import models
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model


def sample_user(email='test@pokemail.net', password='pass3'):
    """Returns a sample user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='beef fry',
            time_minutes=5,
            price=5.90
        )
        self.assertEqual(str(recipe), recipe.title)
