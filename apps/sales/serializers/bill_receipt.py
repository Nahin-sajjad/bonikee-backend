from rest_framework import serializers
from apps.sales.models.bill_receipt import BillReceipt, BillReceiptLineItem
from apps.share.request_middleware import request_local


class BillReceiptLineItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the BillReceiptLineItem model.
    """

    class Meta:
        model = BillReceiptLineItem
        fields = ("id", "created_at", "edited_at", "bill_receipt", "inv_item")

    def to_representation(self, instance):
        """
        Custom representation method for BillReceiptLineItem instances.
        """
        representation = super().to_representation(instance)

        # Additional fields to include in the representation
        representation["qty"] = instance.inv_item.qty if instance.inv_item else None
        representation["per_pack_qty"] = (
            instance.inv_item.per_pack_qty if instance.inv_item else None
        )
        representation["price"] = instance.inv_item.price if instance.inv_item else None
        representation["tax"] = instance.inv_item.tax if instance.inv_item else None
        representation["disc"] = instance.inv_item.tax if instance.inv_item else None
        representation["subtotal"] = (
            instance.inv_item.subtotal if instance.inv_item else None
        )

        request = getattr(request_local, "request", None)
        representation["item_title"] = (
            instance.inv_item.item.item.item_title
            if instance.inv_item.item.item
            else None
        )
        representation["description"] = (
            instance.inv_item.item.item.description
            if instance.inv_item.item.item
            else None
        )

        representation["item_image"] = (
            request.build_absolute_uri(instance.inv_item.item.item.item_image.url)
            if instance.inv_item.item.item.item_image
            else None
        )
        representation["sku"] = (
            instance.inv_item.item.item.sku if instance.inv_item.item.item else None
        )
        representation["unit_name"] = (
            instance.inv_item.unit.uom_name if instance.inv_item.unit else None
        )

        return representation


class BillReceiptSerializer(serializers.ModelSerializer):

    bill_receipt_line_items = BillReceiptLineItemSerializer(many = True, read_only = True)
    """
    Serializer for the BillReceipt model.
    """

    def get_status_list(self, status_value):
        """
        Helper method to map status values to label and style.
        """
        status_choices = {
            1: ["primary", "Open"],
            2: ["secondary", "Partially Paid"],
            3: ["warning", "Fully Paid"],
            4: ["error", "Cancelled"],
            5: ["success", "Delivered"],
        }
        return status_choices.get(status_value, [])

    class Meta:
        model = BillReceipt
        fields = (
            "id",
            "created_at",
            "edited_at",
            "inv",
            "recpt_dt",
            "recpt_amt",
            "bill_receipt_line_items",
            "pay_method",
            "bill_recpt_num",
        )

    def to_representation(self, instance):
        """
        Custom representation method for BillReceipt instances.
        """
        representation = super().to_representation(instance)

        representation["inv_num"] = instance.inv.inv_num if instance.inv else None
        representation["inv_num_label"] = (
            ["primary", instance.inv.inv_num] if instance.inv else None
        )
        representation["bill_recpt_num_label"] = (
            ["primary", instance.bill_recpt_num] if instance else None
        )
        representation["inv_dt"] = (
            instance.inv.inv_dt.strftime("%b %d, %Y") if instance.inv else None
        )
        representation["customer_name"] = (
            instance.inv.cust.customer_name if instance.inv.cust else None
        )
        representation["total_amount"] = (
            instance.inv.total_amount if instance.inv else None
        )
        representation["paid_amount"] = (
            instance.inv.paid_amount if instance.inv else None
        )
        representation["status"] = (
            instance.inv.get_status_display() if instance.inv else None
        )
        representation["status_label"] = self.get_status_list(instance.inv.status)
        representation["recpt_dt"] = (
            instance.recpt_dt.strftime("%b %d, %Y") if instance.recpt_dt else None
        )

        return representation
