from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class VendorTestCase(BaseTestCase):

    def test_list_vendor(self):
        url = reverse("vendor-list")

        for i in range(0, 6):
            self.get_or_create_vendor(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_vendor(self):
        url = reverse('vendor-list')

        data = {
            'tenant': self.tenant.id,
            'vendor_name': "test_vendor_name",
            'phone': '01312345678',
            'address': 'test vendor location',
            'company': 'Glascutr',
            'email': 'example@example.com',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["vendor_name"], "test_vendor_name")
        self.assertEqual(response.data["phone"], "01312345678")
        self.assertEqual(response.data["address"], "test vendor location")
        self.assertEqual(response.data["company"], 'Glascutr')
        self.assertEqual(response.data["email"], 'example@example.com')

    def test_update_vendor(self):
        vendor = self.get_or_create_vendor(15)
        # print(vendor.id)
        url = reverse("vendor-details", kwargs={"pk": vendor.id})

        data = {
            'tenant': self.tenant.id,
            'vendor_name': "test_updated_vendor_name",
            'phone': '01312345679',
            'address': 'test updated vendor location',
            'company': 'Glascutr1fv',
            'email': 'exa@example.com',
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(
            response.data["vendor_name"], "test_updated_vendor_name")
        self.assertEqual(response.data["phone"], "01312345679")
        self.assertEqual(response.data["address"],
                         "test updated vendor location")
        self.assertEqual(response.data["company"], 'Glascutr1fv')
        self.assertEqual(response.data["email"], 'exa@example.com')

    def test_delete_vendor(self):
        vendor = self.get_or_create_vendor(210)
        url = reverse("vendor-details", kwargs={"pk": vendor.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
