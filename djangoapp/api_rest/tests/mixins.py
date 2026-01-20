
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticatedTestMixin:
    def setUp(self):
        super().setUp() 

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'  
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate_client(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def unauthenticate_client(self):
        self.client.credentials()
    