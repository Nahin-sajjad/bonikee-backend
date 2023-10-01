from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class UserRegistrationTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('registration')

        data = {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'test@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }

        response = self.client.post(url, data, format='json')

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['Success'], 'Registration successful')
