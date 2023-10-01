from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class CategoryTestCase(BaseTestCase):

    def test_list_category(self):
        url = reverse("categories")

        for i in range(0, 6):
            self.get_or_create_category(1)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        url = reverse('categories')

        data = {
            'category_name': 'category_name',
            'description': 'description',
            'short_note': 'short_note'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category_name"], "category_name")
        self.assertEqual(response.data["descr"], "description")

    def test_update_category(self):
        category = self.get_or_create_category(1)
        print(category.id)
        url = reverse("category-details", kwargs={"pk": category.id})

        data = {
            'category_name': 'category_name',
            'descr': 'descr',
            'short_note': 'short_note'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.data["category_name"], "category_name")
        self.assertEqual(response.data["descr"], "descr")

    def test_delete_category(self):
        category = self.get_or_create_category(1)
        url = reverse("category-details", kwargs={"pk": category.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
