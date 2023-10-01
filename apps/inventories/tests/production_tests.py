from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class ProductionTestCase(BaseTestCase):

    def test_list_production(self):
        url = reverse("productions")

        for i in range(0, 6):
            self.get_or_create_production(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_create_production(self):
    #     url = reverse('productions')

    #     '''
    #     warehouse_name ="test warehouse",
    #     warehouse_sn = "test warehouse",
    #     location = "Test Gulsion Circle 1",
    #     is_primary = True,
    #     '''
    #     number = 101

    #     data = {

    #         "production_identity": f"test production identity{number}",
    #         "recvd_date":'2023-07-25',
    #         "recvd_qty": 15,
    #         "per_pack_qty": 12,
    #         "non_pack_qty": 6,
    #         "cost_per_unit": 650,
    #         "lot_number": "LOT-420",

    #         "item": self.get_or_create_item(number).id,
    #         "uom": self.get_or_create_uom(number).id,
    #         "recvd_by": self.get_or_create_tenant_user().id,
    #         "recvd_stock": self.get_or_create_warehouse(number).id,
    #         "tenant": self.tenant
    #     }

    #     response = self.client.post(url, data)

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data["warehouse_name"], "test warehouse name")
        # self.assertEqual(response.data["warehouse_sn"], "test warehouse sn")
        # self.assertEqual(response.data["location"], "test warehouse location")
        # self.assertEqual(response.data["is_primary"], True)
        # self.assertNotEqual(response.data["is_primary"], False)

    # def test_update_warehouse(self):
    #     warehouse = self.get_or_create_warehouse(1)
    #     # print(warehouse.id)
    #     url = reverse("warehouse-details", kwargs={"pk": warehouse.id})

    #     data = {
    #         'warehouse_name': 'test updated warehouse  name',
    #         'warehouse_sn': 'test updated warehouse sn',
    #         'location': 'test updated warehouse location',
    #         'is_primary': False,
    #     }

    #     response = self.client.put(url, data)

    #     # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data["warehouse_name"], "test updated warehouse  name")
    #     self.assertEqual(response.data["warehouse_sn"], "test updated warehouse sn")
    #     self.assertEqual(response.data["location"], "test updated warehouse location")
    #     self.assertEqual(response.data["is_primary"], True)

    # def test_delete_warehouse(self):
    #     warehouse = self.get_or_create_warehouse(1)
    #     url = reverse("warehouse-details", kwargs={"pk": warehouse.id})

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

