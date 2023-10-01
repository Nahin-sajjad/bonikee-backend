from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.

    This serializer is used to validate and deserialize data when a user wants
    to change their password.

    Fields:
    - old_password (str): The old/current password.
    - new_password (str): The new password to set.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
