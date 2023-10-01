from django.middleware import csrf
from django.db import transaction

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.users.serializers.registration import RegistrationSerializer
from apps.users.tokens import Tokens

from apps.inventories.models.category import Category

from apps.clients.models import TenantUser

from apps.clients.serializers.tenant_users import TenantUserSerializer
from apps.clients.serializers.tenant import TenantSerializer
from apps.clients.serializers.domain import DomainSerializer

from apps.share.services.error_message_response import error_message_response
from apps.share.services.server_logger import ServerLogger
from apps.share.services.send_email import email_send
from apps.share import constants

from decouple import config


class RegistrationView(CreateAPIView):
    """
    API view for user registration.

    This view allows users to register, creating a new tenant with a unique schema name.

    Methods:
    - POST: Handle user registration.
    """

    permission_classes = (AllowAny,)

    def __init__(self):
        self.response = Response()
        self.tokens = Tokens()
        self.validate = True

    def save_data(self, form_data, serializer_class):
        """
        Save data using the provided serializer.

        Parameters:
        - form_data: Data to be serialized and saved.
        - serializer_class: Serializer class to use for serialization.

        Returns:
        - Serialized and saved data or errors.
        """
        serializer = serializer_class(data=form_data)
        if serializer.is_valid():
            self.validate = True
            return serializer.save()
        else:
            self.validate = False
            return serializer.errors

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.

        Parameters:
        - request: HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - HTTP response indicating the status of the registration.
        """
        try:
            # Check if password and confirm_password match
            if request.data.get("password") == request.data.get("confirm_password"):
                pass
            else:
                error_message = "Confirm password and password must match"
                return error_message_response(
                    error_message=error_message,
                    response=self.response,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save user data
            user_data = self.save_data(request.data, RegistrationSerializer)

            # Save tenant data
            tenant_data = self.save_data(request.data, TenantSerializer)

            if not self.validate:
                error_message = "Schema name exists, must be unique"
                return error_message_response(
                    error_message=error_message,
                    response=self.response,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save domain data
            domain_form_data = {
                "domain": f'{request.data["schema_name"]}.{config("BACKEND_TENANT_DOMAIN")}',
                "tenant": tenant_data.id,
            }

            domain_data = self.save_data(domain_form_data, DomainSerializer)

            if not self.validate:
                error_message = "Domain name exists, must be unique"
                return error_message_response(
                    error_message=error_message,
                    response=self.response,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create tenant_user data
            tenant_user_data = TenantUser.objects.create(
                user=user_data, tenant=tenant_data, is_superuser=True
            )

            # Generate tokens and set cookies
            token_data = self.tokens.get_tokens_for_user(user_data)

            # Generate CSRF token and include it in the response
            csrf_token = csrf.get_token(request)
            message = "Tenant Onboarded Successfully"

            # Include the CSRF token in the response headers
            self.response["X-CSRFToken"] = csrf_token

            # Serialize the response
            domain = DomainSerializer(domain_data).data
            tenant_user = TenantUserSerializer(tenant_user_data).data

            # Return the response
            self.response.data = {
                "message": message,
                "domain_data": domain,
                "tenant_user_data": tenant_user,
                "token_data": token_data,
            }

            # Send an email notification to the user
            email_send(
                request=request,
                subject=constants.TENANT_SUPERUSER_MAIL_SUBJECT,
                message=constants.TENANT_SUPERUSER_MAIL_MESSAGE,
                recipient_list=[user_data.email],
            )

            self.response.status_code = status.HTTP_201_CREATED

        except Exception as e:
            # Handle exceptions here and return an error response
            self.response.data = str(e)
            self.response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            service_logger = ServerLogger()
            service_logger.error(e)

        return self.response
