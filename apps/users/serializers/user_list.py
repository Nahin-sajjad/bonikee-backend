from rest_framework import serializers

from apps.users.models import User


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user data.

    This serializer is used to serialize user data for listing purposes.
    It includes fields such as 'id', 'first_name', 'last_name', 'email', 'date_joined', and 'is_active'.

    Fields:
    - id (int): The unique identifier for the user.
    - first_name (str): The user's first name.
    - last_name (str): The user's last name.
    - email (str): The user's email address.
    - date_joined (datetime): The date and time when the user account was created.
    - is_active (bool): Indicates whether the user account is active or not.

    """

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "date_joined", "is_active")
