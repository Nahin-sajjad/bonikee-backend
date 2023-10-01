from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class ReceiptTestCase(BaseTestCase):

    def test_list_receipt(self):
        url = reverse("receipts")

        for i in range(0, 6):
            self.get_or_create_receipt(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_receipt(self):
        url = reverse('receipts')
        self.number =  313

        data ={
            "recpt_dt": "07/10/2023",
            "ref_number": "213123",
            "vendor": self.get_or_create_vendor(self.number).pk,
            "source": self.get_or_create_warehouse(self.number).pk,
            "grand_total": 2375,
            "receipt_line_items": [
                {
                    "item": self.get_or_create_item(self.number).pk,
                    "lot_number": "Batch 420",
                    "exp_date": "2023-07-25",
                    "unit": self.get_or_create_uom(self.number).pk,
                    "recpt_qty": 50,
                    "per_pack_qty": 0,
                    "price": 50,
                    "commi": 125,
                    "total_amt": 2375
                }
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ref_number"], data['ref_number'])
        self.assertEqual(response.data["vendor"], data['vendor'])
        self.assertEqual(response.data["source"], data['source'] )
        self.assertEqual(response.data["grand_total"], data['grand_total'])


    def test_update_receipt(self):
        self.number =  313
        receipt = self.get_or_create_receipt(1)
        url = reverse("receipt-details", kwargs={"pk": receipt.id})
        for i in range(0, 3):
            self.get_or_create_receipt_line_item(1)

        data ={
            "id": receipt.id,
            "recpt_num": "1-321321-07/10/2023",
            "recpt_dt": "2023-07-10T13:09:57.879204+06:00",
            "ref_number": "321321",
            "vendor": self.get_or_create_vendor(self.number).pk,
            "source": self.get_or_create_warehouse(self.number).pk,
            "grand_total": 95531,
            "receipt_line_items": [
                {
                    "id": self.get_or_create_receipt_line_item(1).pk,
                    "lot_number": "Batch 420",
                    "exp_date": "2023-07-31",
                    "recpt_qty": 50,
                    "per_pack_qty": 0,
                    "price": 500,
                    "commi": 1250,
                    "reciept_identity": "40-Batch 420-0.00",
                    "total_amt": 23750,
                    "tenant": "fc46aab9-1524-4593-9b1d-bd7b4e7f13a0",
                    "item": self.get_or_create_item(self.number).pk,
                    "unit": self.get_or_create_uom(self.number).pk,
                    "unit_name": "Pc",
                    "sub_total": 25000
                }
            ]
        }
        response = self.client.put(url, data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(int(response.data["grand_total"]), int(data['grand_total']))

    def test_delete_recept(self):
        receipt = self.get_or_create_receipt(1)
        url = reverse("receipt-details", kwargs={"pk": receipt.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        
