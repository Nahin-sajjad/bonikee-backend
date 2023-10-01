from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate
from django.middleware import csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventories.models import Category
from apps.users.tokens import Tokens
from apps.users.views.auth.user_log_info import UserLogInfoView
from apps.users.models import User

from apps.clients.models import DomainModel
from apps.clients.serializers.domain import DomainSerializer

from apps.clients.models import TenantUser
from apps.clients.serializers.tenant_users import TenantUserSerializer

from apps.share.services.error_message_response import error_message_response


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(APIView):
    """
    Authenticate user and generate access and refresh tokens as httponly cookies.

    This view allows users to log in and generates access and refresh tokens
    as HTTP-only cookies. It also sets the CSRF token in the response headers.

    Methods:
    - POST: Handle user authentication and token generation.
    """

    permission_classes = [AllowAny]

    def __init__(self, **kwargs: Any) -> None:
        self.tokens = Tokens()
        self.response = Response()

    def post(self, request):
        """
        Handle the POST request for user authentication.

        Args:
        - request: The HTTP request object containing user credentials.

        Returns:
        - Response: JSON response with tokens or an error message with an appropriate status code.
        """
        data = request.data

        email = data.get("email", None)
        password = data.get("password", None)

        # Authenticate the user
        user = authenticate(email=email, password=password)

        if user:
            if not user.is_active:
                error_message = "User is deactivated"
                return error_message_response(
                    error_message=error_message,
                    response=self.response,
                    status=status.HTTP_404_NOT_FOUND,
                )

            tenant_user = TenantUser.objects.get(user=user)
            tenant_data = TenantUserSerializer(tenant_user).data

            domain = DomainModel.objects.get(tenant=tenant_user.tenant)
            domain_data = DomainSerializer(domain).data

            # Generate tokens and set cookies
            token_data = self.tokens.get_tokens_for_user(user)

            try:
                # Create a default category for the tenant
                Category.objects.get_or_create(
                    category_name="General",
                    category_code="GE",
                    tenant=tenant_user.tenant,
                    created_by=user,
                )
            except Exception as e:
                pass

            cookie_settings = {
                "AUTH_COOKIE_SECURE": settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                "AUTH_COOKIE_SAMESITE": settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                "AUTH_COOKIE_HTTP_ONLY": settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            }

            self.tokens.set_cookie(
                response=self.response,
                key=settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS_TOKEN"],
                cookie_settings=cookie_settings,
                token=token_data["access"],
                token_lifetime=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            )

            self.tokens.set_cookie(
                response=self.response,
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_TOKEN"],
                cookie_settings=cookie_settings,
                token=token_data["refresh"],
                token_lifetime=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            )

            # Generate CSRF token and include it in the response
            csrf_token = csrf.get_token(request)

            self.response.data = {
                "Success": "Login successful",
                "data": token_data,
                "tenant_data": tenant_data,
                "domain_data": domain_data,
            }

            # Include the CSRF token in the response headers
            self.response["X-CSRFToken"] = csrf_token
            self.response.status_code = status.HTTP_200_OK

            # Log the login time
            user_log_info_view = UserLogInfoView(user)
            user_log_info_view.login_time(request)

            return self.response

        else:
            # Separate checks for incorrect email and incorrect password
            user_exists = User.objects.filter(email=email).exists()

            if user_exists:
                error_message = "Incorrect Password, The password is incorrect."
                return error_message_response(
                    error_message=error_message,
                    response=self.response,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:
                error_message = "User Not Found, No user with this email exists."
                return error_message_response(
                    error_message=error_message,
                    response=self.response,
                    status=status.HTTP_404_NOT_FOUND,
                )
