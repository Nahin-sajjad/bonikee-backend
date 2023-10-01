from rest_framework import serializers
from apps.hr.models.department import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model.

    This serializer is used to convert Department model instances to JSON representations and vice versa.

    Attributes:
        Meta (class): Configuration class for the serializer.
    """

    class Meta:
        model = Department  # Specifies the model to be serialized
        fields = "__all__"  # Serialize all fields defined in the Department model
