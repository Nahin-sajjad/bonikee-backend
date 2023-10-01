from decouple import config

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import redirect
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from apps.users.models import User

from apps.clients.models import TenantUser

from apps.share.services.send_email import email_send
from apps.share import constants
from apps.share.services.get_client_domain import get_client_login_url


class ForgotPasswordSendResetLinkView(APIView):
    """
    API endpoint for sending a reset password link to a user's email.

    Allows any user, even unauthenticated ones.

    Methods:
    - POST: Send a reset password link to the provided email.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests to send a reset password link.

        Args:
        - request: The HTTP request object containing the email.

        Returns:
        - Response: Success message or error message with appropriate status code.
        """

        email = request.data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        protocol = "https" if request.is_secure() else "http"
        backend_tenant_domain = config("BACKEND_TENANT_DOMAIN")
        if backend_tenant_domain == "localhost":
            activation_link = f"{protocol}://{backend_tenant_domain}:8000/user/forgot/password/{uid}/{token}/"
        else:
            activation_link = f"{protocol}://{backend_tenant_domain}/user/forgot/password/{uid}/{token}/"

        message = constants.FORGOT_PASSWORD_MAIL_MESSAGE.format(activation_link)
        email_send(
            request=request,
            subject=constants.FORGOT_PASSWORD_MAIL_SUBJECT,
            message=message,
            recipient_list=[email],
        )

        return Response("Email sent successfully", status=status.HTTP_200_OK)


class ForgotPasswordActivationLinkView(APIView):
    """
    API endpoint for handling the activation link to reset the password.

    Allows any user, even unauthenticated ones.

    Methods:
    - GET: Handle the activation link and redirect to the reset password page.
    """

    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        """
        Handle GET requests for the activation link.

        Args:
        - request: The HTTP request object.
        - uid: User ID encoded in base64.
        - token: Token for validating the link.

        Returns:
        - HttpResponse: Redirects to the password reset page or returns an error message.
        """

        try:
            user_id = urlsafe_base64_decode(uid).decode("utf-8")
            user = User.objects.get(id=user_id)

            try:
                tenant_user = TenantUser.objects.get(user_id=user.id)
            except TenantUser.DoesNotExist:
                return Response(
                    "Not a valid tenant", status=status.HTTP_400_BAD_REQUEST
                )

            if default_token_generator.check_token(user, token):
                protocol = "https" if request.is_secure() else "http"
                frontend_url = f'{protocol}://{tenant_user.tenant.schema_name}.{config("FRONTEND_TENANT_DOMAIN")}/auth/reset-password/{uid}/{token}/'
                return redirect(frontend_url)
            else:
                return HttpResponse(
                    "Validation Error", status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse("User not valid", status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    API endpoint for resetting a user's password.

    Allows any user, even unauthenticated ones.

    Methods:
    - POST: Reset the user's password and send a confirmation email.
    """

    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        """
        Handle POST requests to reset the user's password.

        Args:
        - request: The HTTP request object.
        - uid: User ID encoded in base64.
        - token: Token for validating the password reset.

        Returns:
        - Response: Success message with appropriate status code or error message.
        """

        try:
            user_id = urlsafe_base64_decode(uid).decode("utf-8")
            user = User.objects.get(id=user_id)

            try:
                tenant_user = TenantUser.objects.get(user_id=user.id)
            except TenantUser.DoesNotExist:
                return Response(
                    "Not a valid tenant", status=status.HTTP_400_BAD_REQUEST
                )

            if default_token_generator.check_token(user, token):
                # Check if the new password and confirmation match
                if request.data.get("password") == request.data.get("password_confirm"):
                    new_password = request.data.get("password")
                    user.set_password(new_password)
                    user.save()
                else:
                    return Response(
                        "Password not matched", status=status.HTTP_400_BAD_REQUEST
                    )

                # Send a confirmation email or return a success response
                message = constants.RESET_PASSWORD_SUCCESFULL_MAIL_MESSAGE
                email_send(
                    request=request,
                    subject=constants.RESET_PASSWORD_SUCCESFULL_MAIL_SUBJECT,
                    message=message,
                    recipient_list=[user.email],
                )
                protocol = "https" if request.is_secure() else "http"
                login_url = get_client_login_url(tenant_user.tenant, protocol)
                return Response(login_url, status=status.HTTP_200_OK)
            else:
                raise ValidationError("Invalid token")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError(
                "Invalid user ID or token", status_code=status.HTTP_400_BAD_REQUEST
            )
