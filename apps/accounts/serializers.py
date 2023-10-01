from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import CustomGroup


from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.

    This serializer is used to serialize Permission objects.

    Attributes:
        model (Model): The model class associated with this serializer.
        fields (tuple): The fields to include in the serialized output.

    Methods:
        get_nested_permissions(permissions): Get nested permissions based on content types.
        to_representation(instance): Customize the serialized representation of a Permission instance.
    """

    class Meta:
        model = Permission
        fields = (
            "id",
            "content_type",
            "codename",
            "name",
        )

    def get_nested_permissions(self, permissions):
        """
        Get nested permissions based on content types.

        Args:
            permissions (QuerySet): A queryset of Permission objects.

        Returns:
            dict: Nested permissions organized by content type categories.
        """

        # Define a mapping of content type categories to permission codenames
        content_type_map = {
            # Mapping of content type categories to permission codenames
            "Product": [
                "item line atribute",
                "stock price",
                "uom",
                "item attribute value",
                "item",
                "category",
                "brand",
                "item attribute",
            ],
            "Inventory": [
                "adjust",
                "warehouse",
                "production",
                "transfer",
                "transfer item",
                "stock",
            ],
            "Finance": [
                "customer collection",
                "customer receivable",
                "inc exp",
                "inc exp type",
                "transaction",
                "vendor pay",
                "vendor payable",
            ],
            "Sales": [
                "bill receipt",
                "bill receipt line item",
                "challan",
                "challan line item",
                "invoice",
                "invoice line item",
                "sale return",
                "sale return line item",
            ],
            "Purchase": [
                "bill pay",
                "bill pay line item",
                "pur return",
                "pur return line item",
                "receipt",
                "receipt line item",
            ],
            "HRM": [
                "advance",
                "attendance",
                "employee",
                "salary",
                "department",
                "designation",
            ],
            "Customer": ["customer"],
            "Vendor": ["vendor"],
            "Account": [],
        }

        # Initialize an empty nested permissions dictionary
        nested_array = {key: [] for key in content_type_map.keys()}

        # Iterate through permissions and categorize them based on content type
        for permission in permissions:
            content_type_name = permission.content_type.name
            serialized_permission = PermissionSerializer(permission).data

            # Check if the content type matches any category, then append the permission
            for key, content_types in content_type_map.items():
                if content_type_name in content_types:
                    nested_array[key].append(serialized_permission)
                    break
            else:
                # If content_type_id doesn't match any category, add to "Account"
                nested_array["Account"].append(serialized_permission)

        return nested_array

    def to_representation(self, instance):
        """
        Customize the serialized representation of a Permission instance.

        Args:
            instance (Permission): The Permission instance to be serialized.

        Returns:
            dict: The customized serialized representation of the instance.
        """
        representation = super().to_representation(instance)
        representation["model_name"] = instance.content_type.name
        return representation


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomGroup model.

    This serializer is used to serialize CustomGroup objects.

    Attributes:
        model (Model): The model class associated with this serializer.
        fields (tuple): The fields to include in the serialized output.

    Methods:
        to_representation(instance): Customize the serialized representation of a CustomGroup instance.
    """

    class Meta:
        model = CustomGroup
        fields = ("id", "name", "users", "permissions")

    def to_representation(self, instance):
        """
        Customize the serialized representation of a CustomGroup instance.

        Args:
            instance (CustomGroup): The CustomGroup instance to be serialized.

        Returns:
            dict: The customized serialized representation of the instance.
        """
        representation = super().to_representation(instance)
        representation["total_user"] = (
            ["primary", instance.users.count()] if instance.users else 0
        )
        return representation
