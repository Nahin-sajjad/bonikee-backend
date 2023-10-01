from rest_framework import serializers
from apps.procurement.models.bill import BillPay, BillPayLineItem


class BillLineItemSerializer(serializers.ModelSerializer):
    """
    Serializer for BillPayLineItem model.
    """

    class Meta:
        model = BillPayLineItem
        fields = ("id", "created_at", "edited_at", "bill", "recpt_item")

    def to_representation(self, instance):
        """
        Customize the representation of BillLineItem instances.
        """
        representation = super().to_representation(instance)
        request = self.context.get("request")

        representation["item"] = (
            instance.recpt_item.item.id if instance.recpt_item.item else None
        )
        representation["sku"] = (
            instance.recpt_item.item.sku if instance.recpt_item.item else None
        )
        representation["recpt_qty"] = (
            instance.recpt_item.recpt_qty if instance.recpt_item else None
        )
        representation["price"] = (
            instance.recpt_item.price if instance.recpt_item else None
        )
        representation["per_pack_qty"] = (
            instance.recpt_item.per_pack_qty if instance.recpt_item else None
        )
        representation["unit_name"] = (
            instance.recpt_item.unit.uom_name if instance.recpt_item.unit else None
        )
        representation["item_brand"] = (
            instance.recpt_item.item.brand.brand_name
            if instance.recpt_item.item.brand
            else None
        )
        representation["item_title"] = (
            instance.recpt_item.item.item_title if instance.recpt_item.item else None
        )
        representation["item_image"] = (
            request.build_absolute_uri(instance.recpt_item.item.item_image.url)
            if instance.recpt_item.item.item_image
            else None
        )
        representation["sub_total"] = (
            instance.recpt_item.total_amt if instance.recpt_item else None
        )
        representation["description"] = (
            instance.recpt_item.item.description if instance.recpt_item.item else None
        )

        return representation


class BillPaySerializer(serializers.ModelSerializer):
    """
    Serializer for BillPay model.
    """

    pays_line_items = BillLineItemSerializer(many=True, read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)

    def get_status_list(self, status_value):
        """
        Get the status label and CSS class based on status value.
        """
        status_choices = {
            1: ["warning", "Partially Bill"],
            2: ["success", "Fully Bill"],
            3: ["error", "Waiting For Bill"],
        }
        return status_choices.get(status_value, [])

    class Meta:
        model = BillPay
        fields = (
            "id",
            "pays_line_items",
            "created_at",
            "edited_at",
            "bill_num",
            "bill_dt",
            "pay_method",
            "adv_amt",
            "bill_amt",
            "status",
            "recpt",
            "cash_amt",
        )

    def to_representation(self, instance):
        """
        Customize the representation of BillPay instances.
        """
        representation = super().to_representation(instance)

        representation["status_label"] = self.get_status_list(instance.status)
        representation["bill_dt"] = (
            instance.bill_dt.strftime("%b %d, %Y") if instance.bill_dt else None
        )
        representation["recpt_num"] = (
            instance.recpt.recpt_num if instance.recpt else None
        )
        representation["recpt_num_label"] = (
            ["primary", instance.recpt.recpt_num] if instance.recpt else None
        )
        representation["bill_num_label"] = (
            ["primary", instance.bill_num] if instance else None
        )
        representation["recpt_dt"] = (
            instance.recpt.recpt_dt.strftime("%b %d, %Y") if instance.recpt else None
        )
        representation["vendor_id"] = (
            instance.recpt.vendor.id if instance.recpt.vendor else None
        )
        representation["vendor_name"] = (
            instance.recpt.vendor.vendor_name if instance.recpt.vendor else None
        )

        return representation
