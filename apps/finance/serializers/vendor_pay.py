from rest_framework import serializers
from apps.finance.models.vendor_pay import VendorPay


class VendorPaySerializer(serializers.ModelSerializer):
    """
    Serializer for VendorPay model.

    This serializer is used to serialize VendorPay objects.

    Attributes:
        model (Model): The model class associated with this serializer.
        fields (tuple): The fields to include in the serialized output.

    Methods:
        to_representation(instance): Customize the serialized representation of a VendorPay instance.
    """

    class Meta:
        model = VendorPay
        fields = (
            "id",
            "vendor",
            "pay_num",
            "amt",
            "note",
            "status",
            "created_at",
            "edited_at",
        )

    def to_representation(self, instance):
        """
        Customize the serialized representation of a VendorPay instance.

        Args:
            instance (VendorPay): The VendorPay instance to be serialized.

        Returns:
            dict: The customized serialized representation of the instance.
        """
        representation = super().to_representation(instance)

        # Add 'vendor_phone' and 'vendor_name' fields if 'vendor' exists
        representation["vendor_phone"] = (
            instance.vendor.phone if instance.vendor else None
        )
        representation["vendor_name"] = (
            instance.vendor.vendor_name if instance.vendor else None
        )

        # Format 'created_at' field as "%b %d, %Y" if it exists
        representation["created_at"] = (
            instance.created_at.strftime("%b %d, %Y") if instance.created_at else None
        )

        return representation
