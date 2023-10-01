from django.conf import settings

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, TokenError


class VerifyToken(APIView):
    """
    API view for verifying the validity of an access token.

    This view allows the verification of an access token to check if it is valid
    and provides information about the token's expiration and refresh token.

    Methods:
    - get: Verify the provided access token and return its status.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Verify the provided access token and return its status.

        Parameters:
        - request: HTTP request object.

        Returns:
        - HTTP response indicating the status of the token.
        """
        access_token = (
            request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS_TOKEN"]) or None
        )
        refresh_token = (
            request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_TOKEN"])
            or None
        )

        if access_token is not None:
            try:
                token_info = AccessToken(access_token)
                response = {
                    "valid": True,
                    "message": "Token is Valid",
                    "exp": token_info["exp"],
                    "refresh": refresh_token,
                }
                return Response(response)

            except TokenError:
                response = {
                    "refresh": refresh_token,
                    "valid": False,
                    "message": "Token is Invalid",
                }
                return Response(response)
        else:
            # Token parameter is missing
            return Response(
                {"valid": False, "message": "Token parameter is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
