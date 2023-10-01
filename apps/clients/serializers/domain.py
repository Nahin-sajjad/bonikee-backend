from rest_framework import serializers
from apps.clients.models import DomainModel

class DomainSerializer(serializers.ModelSerializer):
    """
    Serializer for the DomainModel model.

    This serializer is used to serialize and deserialize DomainModel objects.

    Attributes:
        model (Model): The model class associated with this serializer.
        fields (list or str): The fields to include in the serialized output.
            In this case, it includes all fields using '__all__'.

    Note:
        You can customize the 'fields' attribute to include specific fields if needed.
    """

    class Meta:
        model = DomainModel
        fields = '__all__'
