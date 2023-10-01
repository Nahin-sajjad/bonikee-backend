from rest_framework import serializers

from apps.accounts.models import CustomGroup


class UserGroupInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for user group information.

    This serializer is used to serialize information about custom user groups,
    including their ID, name, and associated permission codenames.

    Fields:
    - id (int): The unique identifier of the user group.
    - name (str): The name of the user group.
    - codename_list (list): A list of codenames of permissions associated with the group.
    """

    class Meta:
        model = CustomGroup
        fields = ["id", "name"]

    def to_representation(self, instance):
        """
        Customize the representation of the serialized data.

        This method adds an additional field to the serialized representation,
        which is a list of permission codenames associated with the group.

        Parameters:
        - instance: The instance of the CustomGroup model being serialized.

        Returns:
        - dict: The serialized representation of the user group.
        """
        representation = super().to_representation(instance)
        permissions = instance.permissions.all()
        representation["codename_list"] = [
            permission.codename for permission in permissions
        ]
        return representation
