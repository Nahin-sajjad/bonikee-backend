from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class TransferTestCase(BaseTestCase):

    def test_list_transfer(self):
        url = reverse("transfer-list")

        for i in range(0, 6):
            self.get_or_create_transfer(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_create_transfer(self):
        url = reverse('transfer-list')

        data = {
            "from_stk": self.get_or_create_warehouse(144).pk,
            "to_stk": self.get_or_create_warehouse(344).pk,
            "date": "07/02/2023, 04:02 PM",
            "purpose_cd": 2,
            "transfers": [
                {
                    "stock": self.get_or_create_stock(10).pk,
                    "trans_qty": 1,
                    "trans_unit": self.get_or_create_uom(404).pk,
                }
            ],
            "primary_stock": [
                {
                    "id": self.get_or_create_stock(10).pk,
                    "stock_identity": "404-10010-1.00",
                    "per_pack_qty": 1,
                    "non_pack_qty": 20,
                    "quantity": 20,
                    "selected_qty": 1,
                    "selected_uom": self.get_or_create_uom(404).pk,
                }
            ],
            "des_stock": [
                {
                    "source": self.get_or_create_warehouse(344).pk,
                    "lot_number": "10010",
                    "exp_date": "2023-06-26",
                    "stock_identity": "404-10010-1.00",
                    "per_pack_qty": 1,
                    "quantity": 1,
                    "non_pack_qty": 1,
                    "uom": self.get_or_create_uom(404).pk,
                    "item": self.get_or_create_item(464).pk,
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['from_stk'], '1')
        self.assertEqual(response.data['to_stk'], '3')

    # def test_update_transfer(self):
    #     transfer = self.get_or_create_transfer(15)
    #     # print(vendor.id)
    #     url = reverse("transfer-details", kwargs={"pk": transfer.id})

    #     data = {
    #         'vendor_name': "test_updated_vendor_name",
    #         'phone': '01312345679',
    #         'address': 'test updated vendor location',
    #         'company': 'Glascutr1fv',
    #         'email': 'exa@example.com',
    #     }

    #     response = self.client.put(url, data)

    #     self.assertEqual(
    #         response.data["vendor_name"], "test_updated_vendor_name")
    #     self.assertEqual(response.data["phone"], "01312345679")
    #     self.assertEqual(response.data["address"],
    #                      "test updated vendor location")
    #     self.assertEqual(response.data["company"], 'Glascutr1fv')
    #     self.assertEqual(response.data["email"], 'exa@example.com')

    # def test_delete_vendor(self):
    #     vendor = self.get_or_create_vendor(210)
    #     url = reverse("vendor-details", kwargs={"pk": vendor.id})

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
