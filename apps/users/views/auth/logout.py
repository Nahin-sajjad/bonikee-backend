from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.users.serializers.logout import LogoutSerializer
from apps.users.views.auth.user_log_info import UserLogInfoView


class LogoutView(GenericAPIView):
    """
    API endpoint for user logout.

    This view handles user logout, invalidates tokens, and deletes cookies.

    Methods:
    - POST: Handle user logout.
    """

    serializer_class = LogoutSerializer

    def post(self, request, *args):
        try:
            # Validate the logout request
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Log the logout time
            user_log_info_view = UserLogInfoView(self.request.user)
            user_log_info_view.logout_time()

            # Perform logout by invalidating tokens and deleting cookies
            serializer.save()

            # Create a response with a custom status code
            response = Response(status=status.HTTP_204_NO_CONTENT)

            # Delete access and refresh token cookies
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response
        except Exception as e:
            # Handle any exceptions and return a custom error response
            print(e)
            return Response(
                {"detail": "Logout failed"}, status=status.HTTP_400_BAD_REQUEST
            )
