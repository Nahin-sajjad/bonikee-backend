from rest_framework import serializers

from apps.inventories.models.brand import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "brand_name", "brand_code")
