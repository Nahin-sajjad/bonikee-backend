from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class ChallanTestCase(BaseTestCase):
    def test_list_challan(self):
        url = reverse('challan')
        for i in range(1, 6):
            self.get_or_create_challan(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_challan(self):
        url = reverse('challan')

        invoice = self.get_or_create_invoice(1)

        data = {
            "invoice_id": invoice.id,
            "challan_number": "123456",
            "challan_date": "2023-07-21T21:09:37.000Z",
            "line_items": [
                {
                    "id": 1,
                    "inv": 1,
                    "item": self.get_or_create_stock(1).id,
                    "qty": 200,
                    "unit": self.get_or_create_uom(1).id,
                    "per_pack_qty": 20,
                    "price": 100,
                    "tax": 10,
                    "disc": 20,
                    "subtotal": 2000,
                    "item_title": "Shirt"
                }
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_challan(self):
        challan = self.get_or_create_challan(1)
        url = reverse("challan_details", kwargs={"pk": challan.id})

        data = {
            "id": 1,
            "invoice_id": 1,
            "customer_name": "test",
            "challan_number": "1234567890",
            "challan_date": "2023-07-21T21:09:37.000Z",
            "ship_to": "test address",
            "discount_amount": 20,
            "tax_amount": 10,
            "total_amount": 2000,
            "paid_amount": 1800,
            "due_amount": 200,
            "line_items": []
        }

        response = self.client.put(url, data, format='json')
        print(response.data)

        self.assertEqual(
            response.data["challan_number"], data['challan_number'])

    def test_delete_challan(self):
        challan = self.get_or_create_challan(1)
        url = reverse("challan_details", kwargs={"pk": challan.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
