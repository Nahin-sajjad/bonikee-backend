from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class AdjustTestCase(BaseTestCase):

    def test_adjust(self):
        url = reverse('adjust')

        item = self.get_or_create_item(1)
        stock = self.get_or_create_stock(1)

        data = {
            "adjust_type_cd": 1,
            "adjust_qty": 100,
            "reason_cd": 1,
            'reason': "test adjust",
            "item": item.id,
            "stock_id": stock.id,
            "new_quantity_on_hand": "101",
            "tenant": self.tenant
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_adjust_list(self):
        url = reverse('adjust')

        for i in range(0, 6):
            self.get_or_create_adjust(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
