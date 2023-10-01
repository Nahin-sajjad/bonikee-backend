from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.category import Category

from apps.inventories.serializers.category import *

from apps.share.views import get_tenant_user
from apps.share.services.generate_short_name import generate_short_name
from django.db import transaction
from apps.share.services.tenant_error_logger import TenantLogger


class CategoryView(generics.ListCreateAPIView):
    queryset = Category
    serializer_class = CategorySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get a list of categories filtered by the current tenant.

        Returns:
            queryset: Queryset containing categories filtered by tenant and parent category.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            try:
                categories = (
                    tenant.category_base_models.filter(cat_parent=None)
                    .select_related("cat_parent")
                    .order_by("created_at")
                )
            except:
                categories = []
            return categories

    @transaction.atomic
    def post(self, request):
        """
        Create a new category.

        This method handles the creation of a new category with optional parent category
        and provides a response with the created category's details.

        Args:
            request (Request): The HTTP POST request containing category data.

        Returns:
            Response: HTTP response containing the created category's details or an error message.
        """
        tenant = get_tenant_user(self).tenant
        tenant_logger = TenantLogger(request)
        try:
            try:
                cat_parent = Category.objects.get(id=request.data.get("cat_parent"))
            except:
                cat_parent = None
            category_code = generate_short_name(request.data.get("category_name"))
            category = Category.objects.create(
                category_name=request.data.get("category_name"),
                category_code=category_code,
                tenant=tenant,
            )
            if category:
                category.descr = request.data.get("description")

                if cat_parent is not None:
                    category.cat_parent = cat_parent  # type: ignore
                category.save()
                return Response(
                    CategorySerializer(category).data, status=status.HTTP_201_CREATED
                )
        except Exception as e:
            tenant_logger.error(e)
            return Response("Tenant not found", status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category
    serializer_class = CategoryByIdSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def perform_update(self, serializer):
        """
        Perform the update of a category.

        This method handles the update of a category, including changing its parent category,
        description, and category code based on the provided data in the request.

        Args:
            serializer (Serializer): The serializer instance responsible for updating the category.

        Returns:
            Category: The updated category instance.
        """
        user_tenant = get_tenant_user(self)
        tenant = user_tenant.tenant
        try:
            cat_parent = Category.objects.get(
                id=self.request.data.get("cat_parent"), tenant=tenant
            )
        except Category.DoesNotExist:
            cat_parent = None
        instance = serializer.save(cat_parent=cat_parent)
        instance.descr = self.request.data.get("descr")
        instance.category_code = generate_short_name(
            self.request.data.get("category_name")
        )
        instance.save()

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        Update a category.

        This method handles the PUT request to update a category and delegates the update operation
        to the `perform_update` method.

        Args:
            request (Request): The HTTP PUT request containing category data.

        Returns:
            Response: HTTP response indicating the success or failure of the update operation.
        """
        print(request.data)
        return self.update(request, *args, **kwargs)
