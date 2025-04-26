from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthViewsTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register') 
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.get_token_url = reverse('get-access-token')

        self.user_data = {
            "email": "testuser@example.com",
            "password": "securepassword123",
            "name": "Test User",
            "phone_number": "1234567890"
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])

    def test_user_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid email or password.")

    def test_logout_user(self):
        user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(user)
        self.client.force_authenticate(user=user)
        response = self.client.post(self.logout_url, {"refresh": str(refresh)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully logged out.")

    def test_logout_without_token(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.post(self.logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully logged out.")

    def test_get_access_token(self):
        user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(user)
        response = self.client.get(self.get_token_url, {"refresh": str(refresh)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_get_access_token_with_invalid_refresh(self):
        response = self.client.get(self.get_token_url, {"refresh": "invalid"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_access_token_missing_refresh(self):
        response = self.client.get(self.get_token_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Refresh token is required.")
        
    def test_logout_user_invalid_token(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)

        invalid_refresh_token = "invalid.token.string"

        response = self.client.post(self.logout_url, {"refresh": invalid_refresh_token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

