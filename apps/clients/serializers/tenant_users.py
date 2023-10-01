from rest_framework import serializers
from apps.clients.models import TenantUser

class TenantUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the TenantUser model.

    This serializer is used to serialize and deserialize TenantUser objects.

    Attributes:
        model (Model): The model class associated with this serializer.
        fields (tuple): The fields to include in the serialized output.
        depth (int): The depth to follow relationships when serializing.

    Methods:
        to_representation(instance): Customize the serialized representation of an instance.
    """

    class Meta:
        model = TenantUser
        fields = ("id", "user", "tenant", "is_superuser")
        depth = 1

    def to_representation(self, instance):
        """
        Customize the serialized representation of a TenantUser instance.

        Args:
            instance (TenantUser): The TenantUser instance to be serialized.

        Returns:
            dict: The customized serialized representation of the instance.
        """
        representation = super().to_representation(instance)
        
        # Include the 'email' field from the related 'user' model
        representation["email"] = instance.user.email
        
        return representation
