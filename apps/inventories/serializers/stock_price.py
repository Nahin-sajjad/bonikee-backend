from rest_framework import serializers
from apps.inventories.models.stock_price import StockPrice
from apps.inventories.models.production import Production


class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['id', 'item', 'markup',
                  'mark_down', 'sales_price', 'min_price', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['item_title'] = instance.item.item_title if instance.item else None
        representation['item_id'] = instance.item.id if instance.item else None
        representation['category_name'] = instance.item.category.category_name if instance.item.category else "No Category"
        representation['brand_name'] = instance.item.brand.brand_name if instance.item.brand else "No Brand"
        representation['unit_name'] = instance.item.uom.uom_name if instance.item.uom else "No Unit"


        return representation
