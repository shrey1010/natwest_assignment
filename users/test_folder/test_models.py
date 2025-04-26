from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
import uuid
class CustomUserManagerTest(TestCase):

    def test_create_user(self):
        email = "user@example.com"
        password = "password123"
        name = "Test User"

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.name, name)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        email = "superuser@example.com"
        password = "password123"
        name = "Super User"

        superuser = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.check_password(password))
        self.assertEqual(superuser.name, name)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError) as context:
            get_user_model().objects.create_user(
                email=None,
                password="password123",
                name="Test User"
            )
        self.assertEqual(str(context.exception), "The Email field must be set")

    def test_create_superuser_without_email(self):
        with self.assertRaises(ValueError) as context:
            get_user_model().objects.create_superuser(
                email=None,
                password="password123",
                name="Super User"
            )
        self.assertEqual(str(context.exception), "The Email field must be set")

    def test_create_user_with_empty_email(self):
        with self.assertRaises(ValueError) as context:
            get_user_model().objects.create_user(
                email="",
                password="password123",
                name="Test User"
            )
        self.assertEqual(str(context.exception), "The Email field must be set")

    def test_create_superuser_with_empty_email(self):
        with self.assertRaises(ValueError) as context:
            get_user_model().objects.create_superuser(
                email="",
                password="password123",
                name="Super User"
            )
        self.assertEqual(str(context.exception), "The Email field must be set")

    def test_unique_email_constraint(self):
        email = "duplicate@example.com"
        password = "password123"
        name = "User One"

        get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email=email,
                password="password456",
                name="User Two"
            )

    def test_username_field(self):
        email = "user@example.com"
        password = "password123"
        name = "Test User"

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertIsNone(user.username)

    def test_custom_id(self):
        email = "user@example.com"
        password = "password123"
        name = "Test User"
        
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertIsInstance(user.id, uuid.UUID)

    def test_phone_number_optional(self):
        email = "user@example.com"
        password = "password123"
        name = "Test User"
        
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name,
            phone_number=None
        )

        self.assertIsNone(user.phone_number)

        user_with_phone = get_user_model().objects.create_user(
            email="user2@example.com",
            password="password123",
            name="Another User",
            phone_number="123456789"
        )

        self.assertEqual(user_with_phone.phone_number, "123456789")
