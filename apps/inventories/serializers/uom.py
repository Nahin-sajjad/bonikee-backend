from rest_framework import serializers

from apps.inventories.models.uom import UOM


class UOMSerializer(serializers.ModelSerializer):

    uom_type = serializers.CharField(source='get_uom_type_cd_display', read_only=True)

    class Meta:
        model = UOM
        fields = ("id", "uom_name", "uom_type_cd","uom_type", "is_pack_unit")
