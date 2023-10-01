from rest_framework import serializers

from apps.inventories.models.item import Item, ItemLineAtribute

import json


class ItemLineAtributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemLineAtribute
        fields = ['id', 'item', 'option_name', 'attributes']


class ItemSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            "id",
            "item_title",
            "description",
            "manufac",
            "item_type_code",
            "item_image",
            "sku",
            "threshold_qty",
            "category",
            "uom",
            "brand",
            "attributes",
        )

    def get_attributes(self, instance):
        item_attributes = ItemLineAtribute.objects.filter(
            item_id=instance.id).first()

        if item_attributes:
            return item_attributes.attributes

        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['category_name'] = instance.category.category_name if instance.category else "No Category Name"

        representation['brand_name'] = instance.brand.brand_name if instance.brand else "No Brand Name"

        representation['uom_name'] = instance.uom.uom_name if instance.uom else "No Uom Name"

        return representation
