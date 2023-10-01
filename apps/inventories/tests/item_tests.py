from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class ItemTestCase(BaseTestCase):

    def test_list_item(self):
        url = reverse("item")

        for i in range(0, 6):
            self.get_or_create_item(i)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_item(self):
        self.get_or_create_category(1)
        self.get_or_create_brand(1)
        self.get_or_create_uom(1)

        url = reverse('item')

        data = {
            'values': ['{"item_type_code":1,"category":1,"description":"<p>Description</p>","item_title":"asdasdasd1","manufac":"Glascutr","uom":1,"sku":"","brand":1,"threshold_qty":1,"attributeList":[],"noOfAttributeSets":1,"submit":null}'],
            'attributeList': ['[{"id":0,"material_description":"23","length":"32"},{"id":1,"material_description":"12","length":"12"}]'],
            'item_image': self.generate_photo()
        }
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_item(self):
        item = self.get_or_create_item(1)
        url = reverse("item-details", kwargs={"pk": item.id})

        data = {
            'item_title': 'title',
            'description': 'description',
            'manufac': 'manufac',
            'item_type_code': '1',
            'item_image': self.generate_photo(),
            'threshold_qty': 1,
            'category': self.get_or_create_category(1).id,
            'uom': self.get_or_create_uom(1).id,
            'brand': self.get_or_create_brand(1).id
        }
        response = self.client.put(url, data, format="multipart")

        self.assertEqual(response.data["item_title"], data['item_title'])
        self.assertEqual(response.data["description"], data['description'])
        self.assertEqual(response.data["manufac"], data['manufac'])
        self.assertEqual(
            response.data["item_type_code"], data['item_type_code'])

    def test_delete_item(self):
        item = self.get_or_create_item(1)
        url = reverse("item-details", kwargs={"pk": item.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
