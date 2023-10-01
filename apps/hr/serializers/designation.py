from apps.hr.models.designation import Designation
from rest_framework import serializers


class DesignationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Designation model.

    This serializer is used to convert Designation model instances to JSON representations and vice versa.

    Attributes:
        Meta (class): Configuration class for the serializer.
    """

    class Meta:
        model = Designation  # Specifies the model to be serialized
        fields = "__all__"  # Serialize all fields defined in the Designation model
