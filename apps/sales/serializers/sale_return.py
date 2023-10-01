from rest_framework import serializers

from apps.sales.models.sale_return import SaleReturn, SaleReturnLineItem


class SaleReturnLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReturnLineItem
        fields = [
            "id",
            "sale_ret",
            "inv_item",
            "ret_qty",
            "ret_amount",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["item"] = instance.inv_item.item.id
        representation["item_title"] = instance.inv_item.item.item.item_title
        representation["qty"] = instance.inv_item.qty
        representation["per_pack_qty"] = instance.inv_item.per_pack_qty
        representation["price"] = instance.inv_item.price
        representation["subtotal"] = instance.inv_item.subtotal
        representation["uom_name"] = instance.inv_item.unit.uom_name
        return representation


class SaleReturnSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="inv.get_status_display", read_only=True)

    class Meta:
        model = SaleReturn
        fields = ["id", "inv", "ret_dt", "ret_amount", "note", "ref", "status"]

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
        representation["return_no"] = instance.inv.inv_num
        representation["customer"] = instance.inv.cust.customer_name
        representation["customer_address"] = instance.inv.cust.address
        representation["total_amount"] = instance.inv.total_amount
        representation["sales_date"] = instance.inv.inv_dt.strftime("%b %d, %Y")
        representation["invoice_date"] = instance.inv.inv_dt
        # representation["status"] = self.get_status_display(instance.inv.status)
        representation["status_list"] = self.get_status_list(instance.inv.status)
        line_items = SaleReturnLineItem.objects.filter(sale_ret_id=instance.id)
        line_items_serializer = SaleReturnLineItemSerializer(line_items, many=True)
        representation["line_items"] = line_items_serializer.data
        return representation
