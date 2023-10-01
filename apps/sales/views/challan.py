from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.sales.models.challan import Challan, ChallanLineItem
from apps.sales.serializers.challan import ChallanSerializer, ChallanLineItemSerializer

from apps.sales.models.invoice import Invoice

from apps.share.views import validate_tenant_user
from apps.share.services.tenant_error_logger import TenantLogger


class ChallanView(generics.ListCreateAPIView):
    """
    API view for listing and creating Challan objects.

    Attributes:
        queryset (QuerySet): The queryset for Challan objects.
        serializer_class (Serializer): The serializer class for Challan objects.
    """

    queryset = Challan
    serializer_class = ChallanSerializer
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

    def get_queryset(self):
        """
        Get the list of Challan objects filtered by the current user's tenant.

        Returns:
            QuerySet: Filtered queryset of Challan objects.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            try:
                return self.tenant.challan_base_models.all().order_by("-created_at")
            except Exception as e:
                # Handle any exceptions that might occur during queryset retrieval.
                TenantLogger.log_error(e)
                return Challan.objects.none()
        else:
            # Return a 404 response if the tenant is not found or valid.
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Create a new Challan object with associated line items.

        Args:
            request (Request): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: HTTP response indicating success or failure.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            line_items = request.data.get("line_items", [])
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                challan = serializer.save(
                    invoice_id=request.data.get("invoice_id", None), tenant=self.tenant
                )
                if challan:
                    Invoice.objects.filter(id=challan.invoice_id).update(status=5)
                    challan_line_item_serializer = ChallanLineItemSerializer(
                        data=line_items, many=True
                    )
                    if challan_line_item_serializer.is_valid():
                        challan_line_item_serializer.save(
                            challan=challan, tenant=self.tenant
                        )
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )  # Consider raising exceptions and providing more specific error messages.
        else:
            return Response("Tenant not valid", status=status.HTTP_404_NOT_FOUND)


class ChallanDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a Challan object.

    Attributes:
        queryset (QuerySet): The queryset for Challan objects.
        serializer_class (Serializer): The serializer class for Challan objects.
    """

    queryset = Challan
    serializer_class = ChallanSerializer
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

    def get_object(self):
        """
        Retrieve a Challan object based on the provided ID and user's tenant.

        Returns:
            Challan: The retrieved Challan object.
        """
        valid = validate_tenant_user(self.tenant, self.request.user)
        if valid:
            try:
                challan_id = self.kwargs.get("pk")
                challan = self.tenant.challan_base_models.get(id=challan_id)
                return challan
            except:
                return Challan.objects.none()
        else:
            # Return a 404 response if the tenant is not found or valid.
            return Response("Tenant not found", status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Update a Challan object and its associated line items.

        Args:
            request (Request): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: HTTP response indicating success or failure.
        """
        instance = self.get_object()
        line_items = request.data.get("line_items", [])
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            challan = serializer.save(
                invoice_id=request.data.get("invoice_id", None), tenant=self.tenant
            )
            for line_item in line_items:
                line_item_id = line_item.get("id")
                challan_line_item = ChallanLineItem.objects.get(id=line_item_id)
                challan_line_item_serializer = ChallanLineItemSerializer(
                    challan_line_item, data=line_item
                )
                if challan_line_item_serializer.is_valid():
                    challan_line_item_serializer.save(
                        challan=challan, tenant=self.tenant
                    )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Consider raising exceptions and providing more specific error messages.

    def perform_destroy(self, instance):
        """
        Perform the deletion of a Challan object.

        Args:
            instance (Challan): The Challan object to be deleted.
        """
        return super().perform_destroy(instance)
