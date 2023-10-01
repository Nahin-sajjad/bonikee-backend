from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class UserLoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='test',
            last_name='user',
            email='test@example.com',
            password='testpassword',
        )

    def test_user_login(self):
        url = reverse('login')

        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
        }

        response = self.client.post(url, data, format='json')

        if response.status_code != 202:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['Success'], 'Login successful')
