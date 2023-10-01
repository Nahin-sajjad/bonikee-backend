from rest_framework import serializers

from apps.users.models import User


class ForgotPasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for requesting a password reset email.

    This serializer is used to validate and deserialize data when a user
    wants to request a password reset email. It includes the user's email
    address.

    Fields:
    - email (str): The email address of the user who wants to reset their password.
    """

    class Meta:
        model = User
        fields = ["email"]
