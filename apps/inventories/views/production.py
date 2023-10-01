from django.db import transaction
from django.forms.models import model_to_dict

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.production import Production
from apps.inventories.serializers.production import ProductionSerializer

from apps.share.views import validate_tenant_user
from apps.share.services.stock_common import stock_exists_obj
from apps.share.services.stock_manager import StockManager
from apps.share.services.tenant_error_logger import TenantLogger


class ProductionView(generics.ListCreateAPIView):
    """
    View for listing and creating Production objects.
    """

    queryset = Production
    serializer_class = ProductionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def dispatch(self, request, *args, **kwargs):
        self.response = Response()
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get a queryset of Production objects for the current tenant.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            production = self.tenant.production_base_models.all()
            return production
        else:
            return Production.objects.none()

    @transaction.atomic
    def post(self, request):
        """
        Create a new Production object.
        """
        data = request.data
        serializer = self.get_serializer(data=data)

        # Tenant logger class for logging error messages
        tenant_logger = TenantLogger(self.request)

        if serializer.is_valid():
            production_identity = f"{data['uom']}-{data['lot_number']}-{'{:.2f}'.format(float(data['per_pack_qty']))}-{data['exp_date']}"
            production_obj = serializer.save(
                tenant=self.tenant, production_identity=production_identity
            )
            production_dict = model_to_dict(production_obj)
            stock_exists_obj(self.tenant, production_dict, production_identity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Handle serializer validation errors and log them
            tenant_logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductionDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a Production object.
    """

    queryset = Production
    serializer_class = ProductionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        """
        Get the Production object for the specified 'pk'.
        """
        production_id = self.kwargs.get("pk")
        production = self.queryset.objects.get(id=production_id)
        return production

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        Update a Production object.
        """
        data = self.request.data
        production = self.get_object()

        # Tenant logger class for logging error messages
        tenant_logger = TenantLogger(self.request)

        current_obj_tenant = self.get_object().tenant
        if self.request.tenant:
            if current_obj_tenant == self.request.tenant:
                serializer = self.get_serializer(production, data=data)
                if serializer.is_valid():
                    production_identity = f"{data['uom']}-{data['lot_number']}-{'{:.2f}'.format(float(data['per_pack_qty']))}-{data['exp_date']}"
                    production_obj = serializer.save(
                        production_identity=production_identity
                    )
                    production_dict = model_to_dict(production_obj)
                    stock_exists_obj(
                        self.request.tenant, production_dict, production_identity
                    )
                else:
                    # Handle serializer validation errors and log them
                    tenant_logger.error(serializer.errors)
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Handle unauthorized access or invalid tenant cases
                return Response("Tenant Not Found", status=status.HTTP_401_UNAUTHORIZED)
        return super().put(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        Delete a Production object.
        """
        # Tenant logger class for logging error messages
        tenant_logger = TenantLogger(self.request)
        current_obj_tenant = self.get_object().tenant
        if self.request.tenant == current_obj_tenant:
            try:
                stock = self.request.tenant.stock_base_models.filter(
                    stock_identity=instance.production_identity,
                    source=instance.recvd_stock,
                    item=instance.item,
                ).last()
                stock_manager = StockManager(stock.id)
                new_quantity_on_hand = stock.quantity - instance.recvd_qty
                stock_manager.stock_create_or_update({"quantity": new_quantity_on_hand})
                return super().perform_destroy(instance)
            except Exception as e:
                tenant_logger.error(e)
                return Response(str(e))
        else:
            # Handle permission denied case
            raise Exception("Permission Denied to delete this production")
