from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class BillPayTestCase(BaseTestCase):

    def test_list_bill_pay(self):
        url = reverse("bill-pay-list")

        for i in range(0, 6):
            self.get_or_create_bill_pay(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_bill_pay(self):
        url = reverse('bill-pay-list')

        data = {
            "recpt": self.get_or_create_receipt(1).pk,
            "status": 2,
            "pay_method": 1,
            "bill_amt": 63920,
            "adv_amt": 63920,
            "cash": 0,
            "pays_line_items": [
                {
                    "recpt_item": 1
                },
                {
                    "recpt_item": 2
                },
                {
                    "recpt_item": 4
                },
                {
                    "recpt_item": 5
                }
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_bill_pay(self):
        bill_pay = self.get_or_create_bill_pay(1)
        url = reverse("bill-pay-details", kwargs={"pk": bill_pay.id})

        data = {
            "id": self.get_or_create_bill_pay(1).pk,
            "bill_num": "1-63920-1",
            "recpt": 1,
            "status": 2,
            "pay_method": "1",
            "bill_amt": 63920,
            "adv_amt": 63920
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.data["bill_num"], data['bill_num'])
        self.assertEqual(response.data["pay_method"], data['pay_method'])
        self.assertEqual(response.data["bill_amt"], data['bill_amt'])
        self.assertEqual(
            response.data["adv_amt"], data['adv_amt'])

    def test_delete_bill_pay(self):
        bill_pay = self.get_or_create_bill_pay(1)
        url = reverse("bill-pay-details", kwargs={"pk": bill_pay.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)