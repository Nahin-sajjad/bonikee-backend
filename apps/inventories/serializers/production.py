from rest_framework import serializers

from apps.inventories.models.production import Production


class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = ["id", "production_identity", "exp_date", "recvd_date", "recvd_qty", "per_pack_qty",
                  "cost_per_unit", "lot_number", "sku", "item", "uom", "recvd_by", "recvd_stock", "edited_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation["item_title"] = instance.item.item_title
        representation["item_sku"] = instance.item.sku
        representation["item_description"] = instance.item.description
        representation['item_image'] = request.build_absolute_uri(
            instance.item.item_image.url) if instance.item.item_image else None
        representation["uom_name"] = instance.uom.uom_name if instance.uom else None
        representation["recvd_date"] = instance.recvd_date.strftime(
            "%b %d, %Y")
        representation["exp_date"] = instance.exp_date.strftime("%b %d, %Y")
        return representation
