from django.utils.text import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logging a user out by blacklisting a refresh token.

    This serializer is used for logging out a user by blacklisting their
    refresh token. It takes a refresh token as input.

    Fields:
    - refresh_token (str): The refresh token to be blacklisted.

    Default Error Messages:
    - bad_token: Message displayed when the provided token is invalid or expired.
    """

    refresh_token = serializers.CharField()

    default_error_messages = {"bad_token": _("Token is invalid or expired")}

    def validate(self, attrs):
        """
        Validate the input data.

        This method validates the input data by checking if the refresh token
        is provided.

        Parameters:
        - attrs (dict): The input data.

        Returns:
        - dict: The validated input data.
        """
        self.token = attrs["refresh_token"]
        return attrs

    def save(self, **kwargs):
        """
        Blacklist the provided refresh token.

        This method attempts to blacklist the provided refresh token. If the
        token is invalid or expired, it raises a TokenError with the message
        "bad_token".

        Raises:
        - TokenError: When the provided token is invalid or expired.
        """
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")
