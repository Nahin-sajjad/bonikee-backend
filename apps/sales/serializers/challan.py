from rest_framework import serializers

from apps.sales.models.challan import Challan, ChallanLineItem


class ChallanLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallanLineItem
        fields = [
            "id",
            "challan",
            "item",
            "unit",
            "qty",
            "per_pack_qty",
            "price",
            "tax",
            "disc",
            "subtotal",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["item_title"] = instance.item.item.item_title
        representation["unit_name"] = instance.unit.uom_name
        return representation


class ChallanSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="invoice.get_status_display", read_only=True)

    class Meta:
        model = Challan
        fields = ["id", "challan_number", "challan_dt", "invoice", "status"]

    def get_status_list(self, status_value):
        status_choices = {
            1: ["primary", "Open"],
            2: ["secondary", "Partially Paid"],
            3: ["warning", "Fully Paid"],
            4: ["error", "Cancelled"],
            5: ["success", "Delivered"],
        }
        return status_choices.get(status_value, [])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["invoice_number"] = instance.invoice.inv_num
        representation["invoice_status"] = instance.invoice.status
        representation["challan_dt"] = instance.challan_dt.strftime("%b %d, %Y")
        representation["discount_amount"] = instance.invoice.discount_amount
        representation["tax_amount"] = instance.invoice.tax_amount
        representation["total_amount"] = instance.invoice.total_amount
        representation["paid_amount"] = instance.invoice.paid_amount
        representation["due_amount"] = instance.invoice.due_amount
        representation["contact"] = instance.invoice.cust.phone
        representation["customer_name"] = instance.invoice.cust.customer_name
        representation["customer_address"] = instance.invoice.cust.address
        representation["total_amount"] = instance.invoice.total_amount
        representation["status_list"] = self.get_status_list(instance.invoice.status)
        representation["invoice_date"] = instance.invoice.inv_dt
        line_items = ChallanLineItem.objects.filter(challan_id=instance.id)
        serializer = ChallanLineItemSerializer(line_items, many=True)
        representation["line_items"] = serializer.data
        return representation
