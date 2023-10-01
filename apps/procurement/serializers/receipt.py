from rest_framework import serializers
from apps.procurement.models.receipt import Receipt, ReceiptLineItem


class ReceiptLineItemSerializer(serializers.ModelSerializer):
    """
    Serializer for ReceiptLineItem model.
    """

    class Meta:
        model = ReceiptLineItem
        fields = "__all__"

    def to_representation(self, instance):
        """
        Customize the representation of ReceiptLineItem instances.
        """
        representation = super().to_representation(instance)
        request = self.context.get("request")

        representation["item_title"] = (
            instance.item.item_title if instance.item else None
        )
        representation["sku"] = instance.item.sku if instance.item else None

        representation["item_image"] = (
            request.build_absolute_uri(instance.item.item_image.url)
            if instance.item.item_image
            else None
        )

        representation["description"] = (
            instance.item.description if instance.item else None
        )
        representation["item_brand"] = (
            instance.item.brand.brand_name if instance.item.brand else None
        )
        representation["unit_name"] = instance.unit.uom_name if instance.unit else None

        return representation


class ReceiptSerializer(serializers.ModelSerializer):
    """
    Serializer for Receipt model.
    """

    receipt_line_items = ReceiptLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = "__all__"

    def to_representation(self, instance):
        """
        Customize the representation of Receipt instances.
        """
        representation = super().to_representation(instance)
        tenant = instance.tenant
        bill = tenant.billpay_base_models.filter(recpt=instance).last()
        representation["recpt_dt"] = instance.recpt_dt.strftime("%b %d, %Y")

        representation["vendor_name"] = (
            instance.vendor.vendor_name if instance.vendor else None
        )
        representation["vendor_address"] = (
            instance.vendor.address if instance.vendor else None
        )

        representation["warehouse_name"] = (
            instance.source.warehouse_name if instance.source else None
        )
        representation["recvd_by_email"] = (
            instance.recvd_by.email if instance.recvd_by else None
        )

        receipt_line_items = representation.pop("receipt_line_items", None)
        representation["receipt_line_items"] = (
            receipt_line_items if receipt_line_items else None
        )
        representation["total_amt"] = instance.grand_total if instance else None
        representation["adv_amt"] = bill.adv_amt if bill else None
        representation["grand_total_price"] = (
            ["success", instance.grand_total] if instance else 0
        )
        representation["recpt_num_chip"] = (
            ["primary", instance.recpt_num] if instance else None
        )

        return representation
