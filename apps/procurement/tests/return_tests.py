
from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class PurReturnTestCase(BaseTestCase):

    def test_list_pur_return(self):
        url = reverse("returns")

        for i in range(0, 6):
            self.get_or_create_pur_return(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_pur_return(self):
        url = reverse("returns")

        data = {
                "recpt": self.get_or_create_receipt(1).pk,
                "return_note": "",
                "recpt_dt": "2023-07-12T11:53:45.830635+06:00",
                "source": self.get_or_create_warehouse(1).pk,
                "vendor_name": "Glascutr 1",
                "return_dt": "07/13/2023",
                "return_amt": 89,
                "pur_return_line_items": [
                    {
                        "recpt_qty": 100,
                        "per_pack_qty": 5,
                        "reciept_identity": "40-Lot 47-5.00-2023-07-12",
                        "item": self.get_or_create_item(1).pk,
                        "unit": self.get_or_create_uom(1).pk,
                        "lot_number": "Lot 47",
                        "exp_date": "2023-07-12",
                        "item_title": "Test",
                        "item_description": "",
                        "unit_name": "Pc",
                        "return_qty": "01",
                        "recpt_item": self.get_or_create_receipt_line_item(1).pk,
                        "unit_price": 100,
                        "price": 89,
                        "subtotal": 89
                    }
                ]
            }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_pur_return(self):
        pur_return = self.get_or_create_pur_return(1)
        print(pur_return)
        url = reverse("return-details", kwargs={"pk": pur_return.id})

        data = {
            "id": self.get_or_create_pur_return(1).pk,
            "recpt": self.get_or_create_receipt(1).pk,
            "recpt_num": "1-dsfdsf-07/12/2023",
            "return_num": "2023-1",
            "return_note": "",
            "recpt_dt": "07/12/2023",
            "vendor_name": "Glascutr 1",
            "return_dt": "07/13/2023",
            "return_amt": 890,
            "pur_return_line_items": [
                {
                    'id':self.get_or_create_pur_return_line_item(1).pk,
                    "created_at": "2023-07-13T11:21:05.963254+06:00",
                    "edited_at": "2023-07-13T11:21:05.963254+06:00",
                    "return_qty": "10",
                    "tenant": "fc46aab9-1524-4593-9b1d-bd7b4e7f13a0",
                    "pur_retrn": self.get_or_create_pur_return(1).pk,
                    "recpt_item": self.get_or_create_receipt_line_item(1).pk,
                    "recpt_qty": 100,
                    "per_pack_qty": 5,
                    "reciept_identity": "40-Lot 47-5.00-2023-07-12",
                    "price": 89,
                    "subtotal": 890,
                    "item": self.get_or_create_item(1).pk,
                    "unit": self.get_or_create_uom(1).pk,
                    "lot_number": "Lot 47",
                    "exp_date": "2023-07-12",
                    "unit_price": 100,
                    "item_title": "Test",
                    "item_description": "",
                    "unit_name": "Pc",
                    "qtyCng": -9
                }
            ]
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["return_amt"], data['return_amt'])
        
    def test_delete_pur_return(self):
        pur_return = self.get_or_create_pur_return(1)
        print(pur_return)
        url = reverse("return-details", kwargs={"pk": pur_return.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
