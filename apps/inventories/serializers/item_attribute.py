from rest_framework import serializers

from apps.inventories.models.item_attribute import ItemAttribute, ItemAttributeValue


class ItemAttributeSerializer(serializers.ModelSerializer):

    attribute_option_value = serializers.CharField(source='get_attribute_option_display', read_only=True)

    class Meta:
        model = ItemAttribute
        fields = ("id", "attribute_name", "attribute_option", "attribute_option_value")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            item_attribute_values = ItemAttributeValue.objects.get(
                attribute_id=instance.id)
            representation['attribute_values'] = item_attribute_values.attribute_value
        except:
            representation['attribute_values'] = None
        representation['value'] = ""

        return representation


class ItemAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAttributeValue
        fields = ("id", "attribute", "attribute_value")

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['attribute_name'] = instance.attribute.attribute_name if instance.attribute else None
        return representation
