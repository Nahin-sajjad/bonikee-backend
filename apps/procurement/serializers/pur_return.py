from rest_framework import serializers
from apps.procurement.models.pur_return import PurReturn, PurReturnLineItem


class PurRetLineItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PurReturnLineItem model.
    """

    class Meta:
        model = PurReturnLineItem
        fields = "__all__"

    def to_representation(self, instance):
        """
        Customize the representation of PurRetLineItem instances.
        """
        representation = super().to_representation(instance)
        representation["recpt_qty"] = (
            instance.recpt_item.recpt_qty if instance.recpt_item else None
        )
        representation["per_pack_qty"] = (
            instance.recpt_item.per_pack_qty if instance.recpt_item else None
        )
        representation["reciept_identity"] = (
            instance.recpt_item.reciept_identity if instance.recpt_item else None
        )
        representation["price"] = (
            instance.recpt_item.total_amt / instance.recpt_item.recpt_qty
            if instance.recpt_item
            else None
        )
        representation["subtotal"] = (
            instance.return_qty
            * (instance.recpt_item.total_amt / instance.recpt_item.recpt_qty)
            if instance.recpt_item
            else None
        )
        request = self.context.get("request")

        representation["item"] = (
            instance.recpt_item.item.id if instance.recpt_item.item else None
        )
        representation["unit"] = (
            instance.recpt_item.unit.id if instance.recpt_item.unit else None
        )
        representation["lot_number"] = (
            instance.recpt_item.lot_number if instance.recpt_item else None
        )
        representation["exp_date"] = (
            instance.recpt_item.exp_date if instance.recpt_item else None
        )
        representation["unit_price"] = (
            instance.recpt_item.price if instance.recpt_item else None
        )
        representation["item_title"] = (
            instance.recpt_item.item.item_title if instance.recpt_item.item else None
        )

        representation["item_image"] = (
            request.build_absolute_uri(instance.recpt_item.item.item_image.url)
            if instance.recpt_item.item.item_image
            else None
        )
        representation["sku"] = (
            instance.recpt_item.item.sku if instance.recpt_item.item else None
        )

        representation["description"] = (
            instance.recpt_item.item.description if instance.recpt_item.item else None
        )
        representation["item_brand"] = (
            instance.recpt_item.item.brand.brand_name
            if instance.recpt_item.item.brand
            else None
        )
        representation["unit_name"] = (
            instance.recpt_item.unit.uom_name if instance.recpt_item.unit else None
        )
        return representation


class PurReturnSerializer(serializers.ModelSerializer):
    """
    Serializer for PurReturn model.
    """

    pur_return_line_items = PurRetLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurReturn
        fields = "__all__"

    def to_representation(self, instance):
        """
        Customize the representation of PurReturn instances.
        """
        representation = super().to_representation(instance)
        representation["recpt_num"] = (
            instance.recpt.recpt_num if instance.recpt else None
        )
        representation["recpt_num_label"] = (
            ["primary", instance.recpt.recpt_num] if instance.recpt else None
        )
        representation["return_num_label"] = (
            ["primary", instance.return_num] if instance else None
        )
        representation["recpt_dt"] = (
            instance.recpt.recpt_dt.strftime("%b %d, %Y") if instance.recpt else None
        )
        representation["return_dt"] = (
            instance.return_dt.strftime("%b %d, %Y") if instance else None
        )
        representation["return_amt_label"] = (
            ["error", instance.return_amt] if instance else 0
        )
        representation["vendor_name"] = (
            instance.recpt.vendor.vendor_name if instance.recpt.vendor else None
        )
        representation["vendor_id"] = (
            instance.recpt.vendor.id if instance.recpt.vendor else None
        )

        return representation
