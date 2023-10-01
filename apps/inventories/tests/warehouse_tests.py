from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class WarehouseTestCase(BaseTestCase):

    def test_list_warehouse(self):
        url = reverse("warehouse")

        for i in range(0, 6):
            self.get_or_create_warehouse(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_warehouse(self):
        url = reverse('warehouse')
        '''
        warehouse_name ="test warehouse",
        warehouse_sn = "test warehouse",
        location = "Test Gulsion Circle 1",
        is_primary = True,
        '''
        

        data = {
            'warehouse_name': 'test warehouse name',
            'warehouse_sn': 'test warehouse sn',
            'location': 'test warehouse location',
            'is_primary': True,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["warehouse_name"], "test warehouse name")
        self.assertEqual(response.data["warehouse_sn"], "test warehouse sn")
        self.assertEqual(response.data["location"], "test warehouse location")
        self.assertEqual(response.data["is_primary"], True)
        self.assertNotEqual(response.data["is_primary"], False)

    def test_update_warehouse(self):
        warehouse = self.get_or_create_warehouse(1)
        # print(warehouse.id)
        url = reverse("warehouse-details", kwargs={"pk": warehouse.id})

        data = {
            'warehouse_name': 'test updated warehouse  name',
            'warehouse_sn': 'test updated warehouse sn',
            'location': 'test updated warehouse location',
            'is_primary': False,
        }

        response = self.client.put(url, data)

        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["warehouse_name"], "test updated warehouse  name")
        self.assertEqual(response.data["warehouse_sn"], "test updated warehouse sn")
        self.assertEqual(response.data["location"], "test updated warehouse location")
        self.assertEqual(response.data["is_primary"], True)

    def test_delete_warehouse(self):
        warehouse = self.get_or_create_warehouse(1)
        url = reverse("warehouse-details", kwargs={"pk": warehouse.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

