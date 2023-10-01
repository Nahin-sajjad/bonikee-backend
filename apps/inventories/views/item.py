from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

# Import models and serializers
from apps.inventories.models.item import Item, ItemLineAtribute
from apps.inventories.serializers.item import (
    ItemSerializer,
    ItemLineAtributeSerializer,
)

from apps.inventories.models.stock_price import StockPrice
from apps.inventories.models.category import Category

from apps.share.services.generate_short_name import generate_short_name
from apps.share.services.tenant_error_logger import TenantLogger
from apps.share.views import validate_tenant_user

import json


class GenerateSku:
    """Helper class to generate SKU based on item attributes."""

    def __init__(self, item_title, tenant, category_id, brand_id, attributes):
        self.tenant = tenant
        self.item_title = item_title
        self.category_id = category_id
        self.brand_id = brand_id
        self.attributes = attributes

    # Methods to generate parts of the SKU
    def get_item_title_short_name(self):
        short_name = generate_short_name(self.item_title)
        return short_name

    def get_category_short_name(self):
        category = Category.objects.filter(id=self.category_id).first()
        if category:
            category_code = category.category_code
            return category_code
        else:
            return "NA"

    def get_brand_code(self):
        try:
            brand_code = self.tenant.brand_base_models.get(id=self.brand_id).brand_code
        except:
            brand_code = "NA"
        return brand_code

    def get_attribute(self):
        joined_short_name = ""
        for attribute in self.attributes.get("attribute_list", []):
            short_name = generate_short_name(attribute.get("value", ""))
            joined_short_name += "-" + short_name
        return joined_short_name

    # Generate the final SKU
    def generate_sku(self):
        item_title_short_name = self.get_item_title_short_name()
        category_short_name = self.get_category_short_name()
        brand_short_name = self.get_brand_code()
        attribute = self.get_attribute()

        # Check if any component is "None" and exclude it from the SKU
        components = [
            item_title_short_name,
            category_short_name,
            brand_short_name,
            attribute,
        ]
        filtered_components = [comp for comp in components if comp and comp != "NA"]

        # Join the non-"None" components with "-"
        sku = "-".join(filtered_components)

        return sku


class ItemView(generics.ListCreateAPIView):
    """API view for listing and creating items."""

    queryset = Item
    serializer_class = ItemSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def dispatch(self, request, *args, **kwargs):
        self.tenant = self.request.tenant
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Retrieve the tenant-specific item list for the user
        valid = validate_tenant_user(tenant=self.tenant, user=self.request.user)
        if valid:
            item = (
                self.tenant.item_base_models.all()
                .select_related("category")
                .select_related("uom")
                .select_related("brand")
                .order_by("-created_at")
            )
            return item
        else:
            # Handle the case where tenant id is not found
            return Response("Tenant not found")

    def post(self, request):
        tenant_logger = TenantLogger(request)

        # Handle POST request to create items
        data = request.data

        item_data = data.get("values", None)
        attribute_list = data.get("attributeList", None)
        images = data.getlist("images[]", None)

        item_data = json.loads(item_data)
        attribute_list = json.loads(attribute_list)

        if self.tenant is None:
            # Handle the case where tenant is not found
            tenant_logger.error("Tenant not found.")
            return Response("Tenant not found.", status=status.HTTP_400_BAD_REQUEST)

        category_id = item_data.get("category", None)
        brand_id = item_data.get("brand", None)
        item_data_list = []
        item_line_attribute_data_list = []

        # Loop through attribute list and create items and attributes
        for attribute_number in range(0, len(attribute_list)):
            generate_sku = GenerateSku(
                item_data.get("item_title", ""),
                self.tenant,
                category_id,
                brand_id,
                attribute_list[attribute_number],
            )
            sku = generate_sku.generate_sku()
            item_serializer = self.get_serializer(data=item_data)
            if item_serializer.is_valid():
                try:
                    item_image = images[attribute_number]
                except:
                    item_image = None
                item = item_serializer.save(
                    tenant=self.tenant, sku=sku, item_image=item_image
                )
                item_line_attribute_serializer = ItemLineAtributeSerializer(
                    data=attribute_list[attribute_number]
                )
                if item_line_attribute_serializer.is_valid():
                    item_line_attribute_serializer.save(
                        tenant=self.tenant,
                        item=item,
                        option_name=attribute_list[attribute_number].get(
                            "option_name", ""
                        ),
                        attributes=attribute_list[attribute_number],
                    )
                item_data_list.append(item_serializer.data)
                item_line_attribute_data_list.append(
                    item_line_attribute_serializer.data
                )
                if item_data.get("price", "") == "":
                    StockPrice.objects.create(
                        tenant=self.tenant, item=item, sales_price=0
                    )
                else:
                    StockPrice.objects.create(
                        tenant=self.tenant, item=item, sales_price=item_data["price"]
                    )
            else:
                tenant_logger.error(f"Item serializer error: {item_serializer.errors}")

        return Response(item_data_list, status=status.HTTP_201_CREATED)


class ItemDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting individual items."""

    queryset = Item
    serializer_class = ItemSerializer
    permission_classes = (GroupPermission,)

    def get_object(self):
        # Retrieve the item object based on the provided PK
        item_id = self.kwargs.get("pk")
        try:
            item = self.queryset.objects.get(id=item_id)
            return item
        except Item.DoesNotExist:
            # Handle the case where item does not exist
            return None

    def put(self, request, *args, **kwargs):
        tenant_logger = TenantLogger(request)

        # Handle PUT request to update an item
        data = self.request.data

        tenant = self.get_object().tenant
        if tenant is None:
            # Handle the case where item's tenant is not found
            tenant_logger.error("Tenant not found.")
            return Response("Tenant not found.", status=status.HTTP_400_BAD_REQUEST)

        item_data = data.get("values", None)
        attribute_list = data.get("attributeList", None)
        item_image = data.get("item_image", None)

        item_data = json.loads(item_data)
        attribute_list = json.loads(attribute_list)[0]

        category_id = item_data.get("category", None)
        brand_id = item_data.get("brand", None)

        if self.request.tenant is None:
            # Handle the case where user's tenant is not found
            tenant_logger.error("User's tenant not found.")
            return Response("Tenant not found.", status=status.HTTP_400_BAD_REQUEST)

        if tenant != self.request.tenant:
            # Handle the case where tenant does not match user's tenant
            tenant_logger.error("Tenant does not match user's tenant.")
            return Response("Tenant Not Correct", status=status.HTTP_400_BAD_REQUEST)

        item = self.get_object()
        if item is None:
            # Handle the case where item does not exist
            tenant_logger.error("Item not found.")
            return Response("Item not found.", status=status.HTTP_404_NOT_FOUND)

        item_serializer = self.get_serializer(item, data=item_data)
        if item_serializer.is_valid():
            generate_sku = GenerateSku(
                item_data.get("item_title", ""),
                tenant,
                category_id,
                brand_id,
                attribute_list,
            )
            sku = generate_sku.generate_sku()
            if item_image:
                item_serializer.save(sku=sku, item_image=item_image)
            else:
                item_serializer.save(sku=sku)
            item_line_attribute = ItemLineAtribute.objects.filter(item=item).first()
            item_line_attribute_serializer = ItemLineAtributeSerializer(
                item_line_attribute, data=attribute_list
            )
            if item_line_attribute_serializer.is_valid():
                item_line_attribute_serializer.save(
                    tenant=tenant,
                    item=item,
                    option_name=attribute_list.get("option_name", ""),
                    attributes=attribute_list,
                )
            return Response(item_serializer.data, status=status.HTTP_200_OK)
        else:
            tenant_logger.error(f"Item serializer error: {item_serializer.errors}")
            return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        tenant_logger = TenantLogger(self.request)
        # Handle item deletion
        item_user_tenant = self.get_object().tenant
        if self.request.tenant == item_user_tenant:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            tenant_logger.error("Cannot delete item from a different tenant.")
            return Response(
                "Cannot delete item from a different tenant",
                status=status.HTTP_403_FORBIDDEN,
            )
