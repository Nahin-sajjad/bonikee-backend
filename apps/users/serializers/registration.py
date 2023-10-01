from rest_framework import serializers

from apps.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer is used for creating new user accounts during the registration process.
    It includes fields for email, password, and confirm_password, and performs validation
    to ensure that the email is unique and that the password and confirm_password match.

    Fields:
    - email (str): The email address of the user.
    - password (str): The password for the user.
    - confirm_password (str): A field used to confirm the password by the user.

    Validation:
    - validate_email: Checks if the provided email already exists in the database.
    - validate: Compares the password and confirm_password fields to ensure they match.

    Creation:
    - create: Sets the user's password and saves the user object.
    """

    email = serializers.EmailField(required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password")

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

    def validate(self, attrs):
        """
        Validate the password and confirm_password.

        This method ensures that the password and confirm_password fields match.

        Parameters:
        - attrs (dict): The input data containing password and confirm_password.

        Returns:
        - dict: The validated data.

        Raises:
        - serializers.ValidationError: If password and confirm_password do not match.
        """
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError("Password does not match")

        return attrs

    def create(self, validated_data):
        """
        Create a new user.

        This method sets the user's password and saves the user object.

        Parameters:
        - validated_data (dict): The validated data for creating the user.

        Returns:
        - User: The newly created user object.
        """
        password = validated_data.get("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user
