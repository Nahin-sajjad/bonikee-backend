from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.finance.models.transaction import Transaction
from apps.finance.serializers.transaction import TransactionSerializer

from apps.share.views import validate_tenant_user
from apps.share.services.tenant_error_logger import TenantLogger
from apps.share.services.custom_pagination import CustomPageNumberPagination


class TransactionView(generics.ListAPIView):
    """
    API view for listing and creating transactions.

    Permissions:
    - Users with specific group permissions or superusers can access this view.

    Methods:
    - GET: Retrieve a list of transactions for the current tenant.
    - POST: Create a new transaction.

    Attributes:
    - queryset (QuerySet): The queryset for retrieving transactions.
    - serializer_class (Serializer): The serializer class for transactions.
    """

    queryset = Transaction
    serializer_class = TransactionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )
    pagination_class = CustomPageNumberPagination

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch method to set the 'tenant' attribute from the request.

        Parameters:
        - request: The HTTP request object.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        - Response from the super class dispatch method.
        """
        # Get the tenant from the request (assuming you have middleware to set 'tenant' on the request object).
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get the queryset of transactions based on the tenant and user validation.

        Returns:
        - QuerySet: The queryset of transactions.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            try:
                return self.tenant.transaction_base_models.all().order_by("-created_at")
            except Exception as e:
                # Handle any exceptions that might occur during queryset retrieval and log them.
                TenantLogger.log_error(e)
                return Transaction.objects.none()
        else:
            # Return a 404 response if the tenant is not found or valid.
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)

    # def perform_create(self, serializer):
    #     """
    #     Perform creation of a new transaction.

    #     Parameters:
    #     - serializer: The transaction serializer.

    #     Returns:
    #     - Response with status code 201 for successful creation.
    #     - Response with status code 400 for validation error.
    #     - Response with status code 404 if the tenant is not found or valid.
    #     """
    #     valid = validate_tenant_user(self.tenant, self.request.user)
    #     if valid:
    #         serializer.validated_data["tenant_id"] = self.tenant.id
    #         return super().perform_create(serializer)
    #     else:
    #         # Return a 404 response if the tenant is not found or valid.
    #         return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)


class TransactionDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a transaction.

    Permissions:
    - Users with specific group permissions or superusers can access this view.

    Methods:
    - GET: Retrieve a transaction by its primary key.
    - PUT/PATCH: Update a transaction.
    - DELETE: Delete a transaction.

    Attributes:
    - queryset (QuerySet): The queryset for retrieving transactions.
    - serializer_class (Serializer): The serializer class for transactions.
    """

    queryset = Transaction
    serializer_class = TransactionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        """
        Get the transaction object based on the provided transaction ID.

        Returns:
        - Transaction: The transaction object.
        """
        transaction_id = self.kwargs.get("pk")
        transaction = self.queryset.objects.get(id=transaction_id)
        return transaction

    def perform_update(self, serializer):
        """
        Perform an update on a transaction.

        Parameters:
        - serializer: The transaction serializer.

        Returns:
        - Response with status code 200 for successful update.
        - Response with status code 400 for validation error.
        - Response with status code 401 if the user doesn't have permission to update.
        - Response with status code 404 if the tenant is not found or valid.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        transaction_user_tenant = self.get_object().tenant

        if valid:
            if transaction_user_tenant == self.request.tenant:
                serializer.validated_data["tenant_id"] = self.request.tenant.id
                return super().perform_update(serializer)
            else:
                # Return a 401 response if the user doesn't have permission to update.
                return Response(
                    "You can't update! Not the same tenant.",
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            # Return a 404 response if the tenant is not found or valid.
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """
        Perform the deletion of a transaction.

        Parameters:
        - instance: The transaction instance.

        Returns:
        - Response with status code 204 for successful deletion.
        - Response with status code 401 if the user doesn't have permission to delete.
        - Response with status code 404 if the tenant is not found or valid.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            transaction_user_tenant = self.get_object().tenant
            if self.request.tenant == transaction_user_tenant:
                return super().perform_destroy(instance)
            else:
                # Return a 401 response if the user doesn't have permission to delete.
                return Response(
                    "Don't have permission to delete",
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            # Return a 404 response if the tenant is not found or valid.
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)
