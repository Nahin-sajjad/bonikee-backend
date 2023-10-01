from rest_framework import serializers
from apps.inventories.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model, including related inventory categories.

    This serializer allows representation of a category and its child categories.
    It includes the name of the parent category when available and prevents cyclic dependencies.

    Attributes:
        inv_categories (SerializerMethodField): Serialized related inventory categories.
        cat_parent_name (CharField): The name of the parent category (derived from cat_parent.category_name).
    """

    inv_categories = serializers.SerializerMethodField()
    cat_parent_name = serializers.CharField(
        source="cat_parent.category_name", read_only=True
    )

    def get_inv_categories(self, obj):
        """
        Serialize related inventory categories.

        This method fetches and serializes related inventory categories. It prefetches and selects related data,
        sorts the categories by the length of their relationships, and then uses the CategorySerializer to serialize them.

        Args:
            obj (Category): The Category instance for which to fetch related inventory categories.

        Returns:
            list: A list of serialized related inventory categories.
        """
        inv_categories = (
            obj.inv_categories.all()
            .prefetch_related("cat_parent")
            .select_related("cat_parent")
        )

        # Sort inv_categories by the length of the relationship
        inv_categories = sorted(inv_categories, key=lambda x: x.inv_categories.count())

        serializer = CategorySerializer(inv_categories, many=True, context=self.context)
        return serializer.data

    def to_representation(self, instance):
        """
        Customize the representation of the serialized Category instance.

        This method ensures that visited categories are not duplicated and sorts the child categories based on their relationships.

        Args:
            instance (Category): The Category instance to be serialized.

        Returns:
            dict: The customized representation of the Category instance.
        """
        representation = super().to_representation(instance)
        context = self.context.setdefault("visited_categories", set())

        # Check if the current category has already been visited
        if instance.id in context:
            return representation

        # Add the current category to visited categories
        context.add(instance.id)

        representation["inv_categories"] = sorted(
            representation["inv_categories"],
            key=lambda x: len(x["inv_categories"]),
        )
        return representation

    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
            "descr",
            "inv_categories",
            "category_code",
            "created_at",
            "edited_at",
            "cat_parent",
            "cat_parent_name",
        )


class CategoryByIdSerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model by ID.

    This serializer represents a Category instance with additional information, including the name of the parent category (if available).

    Attributes:
        cat_parent_name (CharField): The name of the parent category (derived from cat_parent.category_name).
    """

    cat_parent_name = serializers.CharField(
        source="cat_parent.category_name", read_only=True
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
            "descr",
            "created_at",
            "edited_at",
            "cat_parent",
            "cat_parent_name",
            "category_code",
        )
