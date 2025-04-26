from django.test import TestCase
from users.serializers import CustomUserSerializer

class CustomUserSerializerTest(TestCase):
    def test_password_not_in_output(self):
        data = {
            "email": "test@example.com",
            "name": "Tester",
            "password": "testpass123",
        }
        serializer = CustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        output_data = CustomUserSerializer(user).data
        self.assertNotIn('password', output_data)

    def test_missing_email(self):
        data = {
            "name": "Tester",
            "password": "testpass123"
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_password(self):
        data = {
            "email": "test@example.com",
            "name": "Tester"
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_invalid_email(self):
        data = {
            "email": "invalid-email",
            "name": "Tester",
            "password": "testpass123"
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
