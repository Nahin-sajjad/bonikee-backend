from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.exceptions import APIException

from apps.users.custom_authentication import CustomAuthentication


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that extends TokenRefreshView.

    This view refreshes the access token and sets it as a cookie along with the
    refresh token.

    Authentication:
    - Custom authentication is used for this view.

    Methods:
    - POST: Refresh the access token and set cookies for both access and refresh tokens.
    """

    authentication_classes = (CustomAuthentication,)
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to refresh the access token and set cookies.

        Args:
        - request: The HTTP request object.

        Returns:
        - Response: JSON response with access and refresh tokens, and cookies set.
        """

        try:
            # Call the parent class's post method to refresh the token
            response_data = super().post(request, *args, **kwargs)

            # Extract the access and refresh tokens from the response
            access_token = response_data.data["access"]
            refresh_token = response_data.data["refresh"]

            # Create a new Response object
            response = Response()

            # Set cookies for both access and refresh tokens
            response.set_cookie("access_token", access_token)
            response.set_cookie("refresh_token", refresh_token)

            # Set the response data with the tokens
            response.data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

            return response

        except APIException as e:
            # Handle API exceptions (e.g., 400 Bad Request)
            return Response(
                {"error": "Token refresh failed", "detail": str(e)},
                status=e.status_code,
            )

        except Exception as e:
            # Handle any other exceptions with a 500 Internal Server Error
            return Response(
                {"error": "Token refresh failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
