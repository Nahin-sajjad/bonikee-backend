from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.adjust import Adjust
from apps.inventories.serializers.adjust import AdjustSerializer

from apps.share.views import validate_tenant_user
from apps.share.services.stock_manager import StockManager
from apps.share.services.tenant_error_logger import TenantLogger


class AdjustView(generics.ListCreateAPIView):
    """
    API view for listing and creating Adjust objects.

    Attributes:
        queryset (QuerySet): The queryset for retrieving Adjust objects.
        serializer_class (Serializer): The serializer class for Adjust objects.
    """

    queryset = Adjust
    serializer_class = AdjustSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to set the 'tenant' attribute on the request.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Keyword arguments.

        Returns:
            HttpResponse: The HTTP response.
        """
        # Get the tenant from the request (assuming you have middleware to set 'tenant' on the request object).
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def manage_stock(self, data):
        """
        Adjust stock quantity based on the provided data.

        Args:
            data (dict): The adjustment data, including stock_id and new_quantity_on_hand.
        """
        stock_manager = StockManager(data["stock_id"])
        obj = stock_manager.adjust(data["new_quantity_on_hand"])
        stock_manager.stock_create_or_update(obj)

    def get_queryset(self):
        """
        Get a queryset of Adjust objects for the current tenant.

        Returns:
            QuerySet: The queryset of Adjust objects.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            adjust_list = (
                self.tenant.adjust_base_models.all()
                .select_related("item")
                .order_by("-created_at")
            )
            return adjust_list
        else:
            return Adjust.objects.none()

    def post(self, request, *args, **kwargs):
        """
        Create a new Adjust object and adjust stock quantity accordingly.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Keyword arguments.

        Returns:
            Response: The HTTP response.
        """
        tenant_logger = TenantLogger(self.request)
        data = self.request.data
        if self.tenant:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(tenant=self.tenant, item_id=data["item"])
                self.manage_stock(data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Handle serializer validation errors and log them
                tenant_logger.error(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Handle case when the tenant is not found
            return Response("Tenant Not Found", status=status.HTTP_404_NOT_FOUND)
