from django.urls import reverse
from rest_framework import status
from apps.share.test.base import BaseTestCase

class InvoiceTestCase(BaseTestCase):
    def test_list_invoices(self):
        url = reverse('invoice')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_invoice(self):
        url = reverse('invoice')
        print('Testing')

        customer = self.get_or_create_customer(1)
        warehouse = self.get_or_create_warehouse(1)

        line_items = [
            {
                'item': self.get_or_create_stock(1).pk,
                'qty': 5,
                'item_id': self.get_or_create_stock(2).item.pk,
                'unit': self.get_or_create_uom(1).pk,
                'per_pack_qty': 10,
                'price': 50,
                'tax': 5,
                'disc': 0,
                'subtotal': 250
            },
            {
                'item': self.get_or_create_stock(2).pk,
                'qty': self.get_or_create_stock(2).item.pk,
                'item_id': 59,
                'unit': self.get_or_create_uom(1).pk,
                'per_pack_qty': 5,
                'price': 30,
                'tax': 3,
                'disc': 0,
                'subtotal': 90
            }
        ]


        data = {
            'cust': customer.id,
            'bill_to': 'Test Bill To',
            'warehouse': warehouse.id,
            'inv_num': 'Test Invoice Number',
            'inv_dt': '2023-07-16T10:00:00Z',
            'payment_method': 'Test Payment Method',
            'status': 1,
            'discount_amount': 10,
            'tax_amount': 5,
            'total_amount': 340,
            'paid_amount': 300,
            'due_amount': 40,
            'inv_line_items': line_items
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_invoice(self):
        invoice = self.get_or_create_invoice(1)
        url = reverse('invoice_details', args=[invoice.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert response data if needed

    def test_update_invoice(self):
        invoice = self.get_or_create_invoice(1)
        url = reverse('invoice_details', args=[invoice.id])

        line_items = [
            {
                'id': 1,  # Existing line item ID to update
                'item': self.get_or_create_stock(3).id,
                'item_id': self.get_or_create_stock(3).item.pk,
                'qty': 2,
                'unit': self.get_or_create_uom(1).pk,
                'per_pack_qty': 5,
                'price': 20,
                'tax': 2,
                'disc': 0,
                'subtotal': 40
            },
            {
                'item': self.get_or_create_stock(4).pk,
                'item_id': self.get_or_create_stock(3).item.pk,
                'qty': 1,
                'unit': self.get_or_create_uom(1).pk,
                'per_pack_qty': 2,
                'price': 15,
                'tax': 1.5,
                'disc': 0,
                'subtotal': 15
            }
        ]

        data = {
            'inv_num': 'Updated Invoice Number',
            'status': 2,
            'inv_line_items': line_items
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert updated fields in the response or retrieve the updated invoice from the database and assert its fields

    def test_delete_invoice(self):
        invoice = self.get_or_create_invoice(1)
        url = reverse('invoice_details', args=[invoice.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Assert the invoice is deleted from the database

