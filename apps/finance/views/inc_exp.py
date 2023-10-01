from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.finance.models.inc_exp import IncExp
from apps.finance.serializers.inc_exp import IncExpSerializer

from apps.share.views import validate_tenant_user, number_generate
from apps.share.services.tenant_error_logger import TenantLogger
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class IncExpView(generics.ListCreateAPIView):
    """
    API view for listing and creating IncExp (Income/Expense) objects.

    Permissions:
    - Users with specific group permissions or superusers can access this view.

    Methods:
    - GET: Retrieve a list of IncExp objects for the current tenant.
    - POST: Create a new IncExp object and associated transaction.
    """

    queryset = IncExp
    serializer_class = IncExpSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

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
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get a queryset of IncExp objects for the current tenant.

        Returns:
        - Queryset of IncExp objects filtered by tenant.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            try:
                return self.tenant.incexp_base_models.all().order_by("-created_at")
            except:
                return IncExp.objects.none()
        else:
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """
        Create a new IncExp object and associated transaction.

        Parameters:
        - request: The HTTP request object.

        Returns:
        - Response with status code 201 for successful creation.
        - Response with status code 400 for validation error.
        - Response with status code 500 for server error.
        """
        tenant_logger = TenantLogger(request)
        serializer = self.serializer_class(data=request.data)
        source_type = request.data["source_type"]

        if source_type == 1:
            source_type_short_name = "INC"
            tran_group = 101
            tran_head = 5
        elif source_type == 2:
            source_type_short_name = "EXP"
            tran_group = 102
            tran_head = 6

        if self.tenant:
            if serializer.is_valid():
                try:
                    previous_num = (
                        self.tenant.incexp_base_models.filter(source_type=source_type)
                        .last()
                        .num
                    )
                except:
                    previous_num = f"{source_type_short_name}-{datetime.now().year}-{0}"
                num = number_generate(previous_num)
                inc_exp = serializer.save(tenant=self.tenant, num=num)
                transaction_manager = TransactionManager(
                    tran_number=num, tenant=self.tenant
                )
                transaction_manager.transaction_create_or_update(
                    tran_group=tran_group,
                    amount=inc_exp.amt,
                    tran_type=inc_exp.type,
                    tran_head=tran_head,
                )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Handle serializer validation errors and log them
                tenant_logger.error(serializer.error_messages)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Tenant id not found", status=status.HTTP_404_NOT_FOUND)


class IncExpDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting an IncExp object.

    Permissions:
    - Users with specific group permissions or superusers can access this view.

    Methods:
    - GET: Retrieve an IncExp object by its primary key.
    - PUT/PATCH: Update an IncExp object.
    - DELETE: Delete an IncExp object.
    """

    queryset = IncExp
    serializer_class = IncExpSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

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
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        """
        Get the IncExp object for the specified 'pk'.

        Returns:
        - IncExp object or Response with status code 404 if not found.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        inc_exp_id = self.kwargs.get("pk")
        if valid:
            try:
                return self.tenant.incexp_base_models.get(id=inc_exp_id)
            except:
                return Response("IncExp not found", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Update an IncExp object.

        Returns:
        - Response with status code 200 for successful update.
        - Response with status code 400 for validation error.
        - Response with status code 404 if the IncExp object is not found.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an IncExp object.

        Returns:
        - Response with status code 204 for successful deletion.
        - Response with status code 404 if the IncExp object is not found.
        """
        return super().destroy(request, *args, **kwargs)
