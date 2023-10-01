from rest_framework import serializers

from apps.inventories.models.warehouse import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        # fields = ("id", "warehouse_name", "warehouse_sn", "location", "is_primary")
        fields = "__all__"
        depth = 1
