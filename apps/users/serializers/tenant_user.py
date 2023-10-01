from rest_framework import serializers

from apps.users.models import User


class CreateTenantUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tenant users.

    This serializer is used for creating new user accounts for tenants.
    It includes fields for email and password and performs validation to ensure
    that the email is unique.

    Fields:
    - email (str): The email address of the tenant user.
    - password (str): The password for the tenant user.

    Validation:
    - validate_email: Checks if the provided email already exists in the database.

    Creation:
    - create: Sets the user's password and saves the user object.
    - to_representation: Removes the 'password' field from the serialized data.
    """

    class Meta:
        model = User
        fields = ("email", "password")

    def validate_email(self, value):
        """
        Validate the uniqueness of the email.

        This method checks if the provided email address already exists in the database.

        Parameters:
        - value (str): The email address to be validated.

        Returns:
        - str: The validated email address.

        Raises:
        - serializers.ValidationError: If the email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """
        Create a new tenant user.

        This method sets the tenant user's password and saves the user object.

        Parameters:
        - validated_data (dict): The validated data for creating the tenant user.

        Returns:
        - User: The newly created tenant user object.
        """
        password = validated_data.get("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        """
        Serialize the tenant user object, removing the 'password' field.

        This method removes the 'password' field from the serialized data before
        returning it.

        Parameters:
        - instance (User): The tenant user object to be serialized.

        Returns:
        - dict: The serialized data without the 'password' field.
        """
        data = super().to_representation(instance)
        data.pop("password", None)
        return data
