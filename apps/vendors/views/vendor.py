from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.vendors.models.vendor import Vendor
from apps.vendors.serializers.vendor import VendorSerializer

from apps.share.views import get_tenant_user


class VendorView(generics.ListCreateAPIView):
    queryset = Vendor
    serializer_class = VendorSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        # Get the tenant associated with the user making the request
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            # Retrieve and return the list of vendors for the current tenant, ordered by creation date
            vendors = tenant.vendor_base_models.all().order_by("created_at")
            return vendors

    def post(self, request):
        # Get the tenant associated with the user making the request
        user_tenant = get_tenant_user(self)
        tenant = user_tenant.tenant
        # Add the tenant ID to the request data to ensure the vendor is associated with the correct tenant
        request.data["tenant"] = tenant.id
        if user_tenant is not None:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # Save the vendor object with the associated tenant
                serializer.save(tenant=tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VendorDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor
    serializer_class = VendorSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get(self, request, *args, **kwargs):
        # Retrieve and return a vendor's details
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Get the tenant associated with the user making the request
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        # Retrieve the vendor object to be updated

        # Save the updated vendor object with the associated tenant
        vendor_obj = tenant.vendor_base_models.get(id=pk)
        serializer = self.get_serializer(vendor_obj, data=request.data)
        if serializer.is_valid():
            serializer.save(tenant=tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        print(request.data)

    def delete(self, request, *args, **kwargs):
        # Delete a vendor object
        return super().delete(request, *args, **kwargs)
