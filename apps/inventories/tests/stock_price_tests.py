from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class StockPriceTestCase(BaseTestCase):

    def test_list_stock_price(self):
        url = reverse('stock_price')

        for i in range(1, 6):
            self.get_or_create_production(i)
            self.get_or_create_stock_price(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_stock_price(self):
        stock_price = self.get_or_create_stock_price(1)
        url = reverse('stock_price_details', kwargs={"pk": stock_price.id})
        
        data = {
            "id": stock_price.id,
            "stock_id": self.get_or_create_stock(1).id,
            "markup": 0,
            "mark_down": 15,
            'sales_price': 200,
            "min_price": 150,
            "tenant": self.tenant
        }
        
        response = self.client.put(url, data)

        self.assertEqual(response.data["mark_down"], 15)