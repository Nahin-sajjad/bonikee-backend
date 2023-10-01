from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.stock_price import StockPrice
from apps.inventories.serializers.stock_price import StockPriceSerializer

from apps.share.views import validate_tenant_user
from apps.share.services.tenant_error_logger import TenantLogger


class StockPriceView(generics.ListAPIView):
    """
    View for listing StockPrice objects.
    """

    queryset = StockPrice
    serializer_class = StockPriceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def dispatch(self, request, *args, **kwargs):
        # Get the tenant from the request (assuming you have middleware to set 'tenant' on the request object).
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get a queryset of StockPrice objects for the current tenant.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            # Filter and order StockPrice objects for the current tenant.
            stock_prices = self.tenant.stockprice_base_models.all().order_by(
                "-created_at"
            )
            return stock_prices
        else:
            # Return an empty queryset or handle the invalid case as needed.
            return StockPrice.objects.none()


class StockPriceDetailsView(generics.UpdateAPIView):
    """
    View for updating a StockPrice object.
    """

    queryset = StockPrice
    serializer_class = StockPriceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def dispatch(self, request, *args, **kwargs):
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        """
        Get the StockPrice object for the specified 'pk' and user's tenant.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        stock_price_id = self.kwargs.get("pk")
        if valid:
            try:
                stock_price = self.tenant.stockprice_base_models.get(id=stock_price_id)
                return stock_price
            except StockPrice.DoesNotExist:
                return StockPrice.objects.none()
        else:
            return Response("Tenant Not Found", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # tenant logger class for logging error messages
        tenant_logger = TenantLogger(self.request)
        current_obj_tenant = self.get_object().tenant if self.get_object() else None

        if current_obj_tenant == self.tenant:
            serializer = self.serializer_class(
                instance=self.get_object(), data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Handle serializer validation errors.
                tenant_logger.error(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Handle unauthorized access or invalid tenant cases.
            return Response(
                {"detail": "Unauthorized or invalid request."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
