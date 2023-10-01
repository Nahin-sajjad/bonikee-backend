from rest_framework import serializers
from apps.finance.models.customer_collection import CustomerCollection

class CustomerCollectionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CustomerCollection
        fields = ('id', 'collection_num','customer', 'amount', 'note', 'status', 'created_at', 'edited_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
            
        representation['customer_name'] = instance.customer.customer_name if instance.customer else None
        representation['customer_phone'] = instance.customer.phone if instance.customer else None

        representation["created_at"] = (
            instance.created_at.strftime("%b %d, %Y") if instance.created_at else None
        )

        return representation