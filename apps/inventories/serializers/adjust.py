from rest_framework import serializers

from apps.inventories.models.adjust import Adjust


class AdjustSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adjust
        fields = ['id', 'adjust_type_cd', 'adjust_dt',
                  'adjust_qty', 'reason_cd', 'reason', 'created_at', 'edited_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        try:
            representation['item_title'] = instance.item.item_title
            representation['item_description'] = instance.item.description
        except:
            representation['item_title'] = None
            representation['item_description'] = None

        try:
            representation['item_image'] = request.build_absolute_uri(
                instance.item.item_image.url)
        except:
            representation['item_image'] = None

        return representation
