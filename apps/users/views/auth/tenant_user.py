import secrets
import string

from django.db import transaction

from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import GroupPermission

from apps.users.models import User

from apps.clients.models import TenantUser

from apps.users.serializers.tenant_user import CreateTenantUserSerializer

from apps.share.services.send_email import email_send
from apps.share.services.get_client_domain import get_client_login_url
from apps.share import constants


class TenantUserView(ListCreateAPIView):
    """
    API view for creating and listing tenant users.

    This view allows the creation of tenant users and listing existing users.

    Methods:
    - POST: Create a new tenant user.
    """

    queryset = User
    serializer_class = CreateTenantUserSerializer
    permission_classes = (GroupPermission,)

    def dispatch(self, request, *args, **kwargs):
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def generate_password(self):
        """
        Generate a random password.

        Returns:
        - str: A randomly generated password.
        """
        characters = (
            string.ascii_uppercase
            + string.digits
            + string.ascii_lowercase
            + string.punctuation
        )
        password_length = 10
        password = "".join(secrets.choice(characters) for _ in range(password_length))
        return password

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for creating a new tenant user.

        Parameters:
        - request: HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - HTTP response indicating the status of the user creation.
        """
        try:
            data = dict(request.data)
            data["password"] = self.generate_password()
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            TenantUser.objects.create(user=user, tenant=self.tenant)
            protocol = "https" if request.is_secure() else "http"
            login_url = get_client_login_url(self.tenant, protocol)
            message = constants.TENANT_USER_MAIL_MESSAGE.format(
                data["password"], login_url
            )
            email_send(
                request, constants.TENANT_USER_MAIL_SUBJECT, message, [user.email]
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle exceptions here and return an error response
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
