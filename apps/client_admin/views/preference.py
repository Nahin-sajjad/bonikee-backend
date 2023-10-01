import json

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission
from apps.share.services.tenant_error_logger import TenantLogger
from apps.client_admin.models import Preference
from apps.client_admin.serializers.preference import PreferenceSerializer


class PreferenceView(generics.ListCreateAPIView):
    queryset = Preference
    serializer_class = PreferenceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        tenant = self.request.tenant
        if tenant is not None:
            preference = tenant.preference_base_models.last()
            return [preference]

        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        tenant_logger = TenantLogger(request)
        data = json.loads(request.data["values"])
        data["logo"] = request.data["logo"]

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(tenant=request.tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            tenant_logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Preference
    serializer_class = PreferenceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        tenant_logger = TenantLogger(request)
        preference_obj = self.get_object()
        data = json.loads(request.data["values"])
        try:
            data["logo"] = request.data["logo"]
        except KeyError:
            data["logo"] = preference_obj.logo

        serializer = self.get_serializer(preference_obj, data=data)
        if serializer.is_valid():
            serializer.save(tenant=request.tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            tenant_logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
