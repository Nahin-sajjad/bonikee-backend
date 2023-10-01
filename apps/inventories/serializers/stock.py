from rest_framework import serializers

from apps.inventories.models.stock import Stock


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = ['id', 'stock_identity',
                  'per_pack_qty', 'non_pack_qty', 'quantity', 'source', 'item', 'item_price', 'uom', 'lot_number', 'exp_date', 'edited_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        representation['item_title'] = instance.item.item_title if instance.item else None
        representation['item_image'] = request.build_absolute_uri(
            instance.item.item_image.url) if instance.item.item_image else None
        representation['sku'] = instance.item.sku if instance.item else None
        representation['item_description'] = instance.item.description if instance.item else None

        representation['base_unit_name'] = instance.item.uom.uom_name if instance.item.uom else "No Base Unit"
        representation['uom_name'] = instance.uom.uom_name if instance.uom else "No Stock unit"
        representation['is_pack'] = instance.uom.is_pack_unit if instance.uom else False
        representation['base_unit_id'] = instance.item.uom.id if instance.item.uom else None
        representation['base_unit_is_pack'] = instance.item.uom.is_pack_unit if instance.item.uom else False

        representation['price'] = instance.item_price.sales_price if instance.item_price else None

        return representation

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     request = self.context.get('request')
    #
    #     representation['stock_price'] = stock_price.unit_price if stock_price else None

    #     representation['item_title'] = instance.item.item_title if instance.item else None

    #     representation['item_image'] = request.build_absolute_uri(
    #         instance.item.item_image.url) if instance.item.item_image else None

    #     representation['item_description'] = instance.item.description if instance.item else None

    #     representation['uom_name'] = instance.uom.uom_name if instance.uom else None
    #     representation['sku'] = instance.item.sku if instance.item else None
    #     representation['base_unit_id'] = instance.item.uom.id if instance.item.uom else None
    #     representation['base_unit_name'] = instance.item.uom.uom_name if instance.item.uom else None

    #     stock_price = instance.stock_stock_price.first()
    #     try:
    #         tenant = instance.tenant
    #         stock_price = tenant.stockprice_base_models.get(
    #             stock=instance.item)
    #     except:
    #         pass

    #     representation['price'] = stock_price.unit_price if stock_price else None

    #     return representation
