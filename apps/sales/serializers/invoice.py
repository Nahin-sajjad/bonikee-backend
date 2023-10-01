from rest_framework import serializers

from apps.sales.models.invoice import Invoice, InvoiceLineItem
from apps.share.request_middleware import request_local


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = (
            "id",
            "inv",
            "item",
            "qty",
            "unit",
            "per_pack_qty",
            "price",
            "tax",
            "disc",
            "subtotal",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = getattr(request_local, "request", None)

        representation["item_image"] = (
            request.build_absolute_uri(instance.item.item.item_image.url)
            if instance.item.item.item_image
            else None
        )
        representation["item_title"] = (
            instance.item.item.item_title if instance.item.item else None
        )
        representation["description"] = (
            instance.item.item.description if instance.item.item else None
        )
        representation["sku"] = instance.item.item.sku if instance.item.item else None
        representation["unit_name"] = instance.unit.uom_name if instance.unit else None

        return representation


class InvoiceSerializer(serializers.ModelSerializer):
    invoice_line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id",
            "cust",
            "warehouse",
            "bill_to",
            "inv_num",
            "status",
            "inv_dt",
            "payment_method",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "paid_amount",
            "due_amount",
            "invoice_line_items",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        line_items = InvoiceLineItem.objects.filter(inv_id=instance.id)
        serializer = InvoiceLineItemSerializer(line_items, many=True)
        representation["line_items"] = serializer.data

        representation["customer_name"] = (
            instance.cust.customer_name if instance.cust else None
        )
        representation["customer_address"] = (
            instance.cust.address if instance.cust else None
        )
        representation["warehouse_name"] = (
            instance.warehouse.warehouse_name if instance.warehouse else None
        )
        representation["inv_dt"] = (
            instance.inv_dt.strftime("%b %d, %Y") if instance.inv_dt else None
        )


        return representation
