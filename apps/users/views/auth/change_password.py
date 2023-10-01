from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException, NotFound

from apps.users.serializers.change_password import ChangePasswordSerializer


class OldPasswordIncorrect(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Old password is incorrect."


class ChangePasswordView(APIView):
    """
    API endpoint for changing a user's password.

    Requires authentication with a valid user token.

    Methods:
    - POST: Change the user's password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests to change the user's password.

        Args:
        - request: The HTTP request object containing user data.

        Returns:
        - Response: JSON response indicating success or error.
        """

        # Deserialize the incoming data using the ChangePasswordSerializer
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check if the old password matches the user's current password
            if not request.user.check_password(
                serializer.validated_data["old_password"]
            ):
                raise OldPasswordIncorrect()

            # Set the new password and save it
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save()

            return Response(
                {"message": "Password changed successfully."}, status=status.HTTP_200_OK
            )

        # If the serializer is not valid, return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, NotFound):
            return Response(
                {"message": "Resource not found."}, status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, APIException):
            return Response({"message": str(exc)}, status=exc.status_code)
        else:
            return super().handle_exception(exc)
