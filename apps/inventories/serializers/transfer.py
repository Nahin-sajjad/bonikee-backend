from rest_framework import serializers

from apps.inventories.models.transfer import Transfer, TransferItem
from apps.inventories.models.item import ItemLineAtribute


class TransferItemSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = TransferItem
        fields = ("id", "stock", "trans_qty", "trans_unit", "attributes")

    def get_attributes(self, instance):
        """
        Retrieve attributes for the TransferItem.

        This method fetches the attributes associated with the TransferItem from the related ItemLineAttribute,
        if available.

        Args:
            instance (TransferItem): The TransferItem instance for which to fetch attributes.

        Returns:
            dict: A dictionary representing the attributes, or None if no attributes are found.
        """
        item_attributes = ItemLineAtribute.objects.filter(item_id=instance.id).first()

        if item_attributes:
            return item_attributes.attributes

        return None

    def to_representation(self, instance):
        """
        Customize the representation of the serialized TransferItem instance.

        This method adds additional information to the serialized TransferItem representation, such as item details,
        stock details, and more.

        Args:
            instance (TransferItem): The TransferItem instance to be serialized.

        Returns:
            dict: The customized representation of the TransferItem instance.
        """
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # Fetch destination stock
        instance.des_stock = instance.tenant.stock_base_models.get(
            source=instance.transfer.to_stk,
            stock_identity=instance.des_stock_identity,
            item_id=instance.stock.item.id,
        )

        # Add item-related information to the representation
        representation["item"] = instance.stock.item.id if instance.stock.item else None
        representation["sku"] = instance.stock.item.sku if instance.stock.item else None
        representation["item_title"] = (
            instance.stock.item.item_title if instance.stock.item else None
        )
        representation["item_image"] = (
            request.build_absolute_uri(instance.stock.item.item_image.url)
            if instance.stock.item.item_image
            else None
        )
        representation["description"] = (
            instance.stock.item.description if instance.stock.item else None
        )

        # Add uom-related information to the representation
        representation["uom_name"] = (
            instance.stock.uom.uom_name if instance.stock.uom else None
        )
        representation["uom_id"] = instance.stock.uom.id if instance.stock.uom else None
        representation["base_uom_id"] = (
            instance.stock.item.uom.id if instance.stock.item.uom else None
        )
        representation["base_uom_name"] = (
            instance.stock.item.uom.uom_name if instance.stock.item.uom else None
        )
        representation["trans_uom_name"] = (
            instance.trans_unit.uom_name if instance.trans_unit else None
        )

        # Add stock-related information to the representation
        representation["stock_identity"] = (
            instance.stock.stock_identity if instance.stock else None
        )
        representation["per_pack_qty"] = (
            instance.stock.per_pack_qty if instance.stock else None
        )
        representation["quantity"] = instance.stock.quantity if instance.stock else None
        representation["non_pack_qty"] = (
            instance.stock.non_pack_qty if instance.stock else None
        )
        representation["lot_number"] = (
            instance.stock.lot_number if instance.stock else None
        )
        representation["exp_date"] = instance.stock.exp_date if instance.stock else None

        # Add transfer-related information to the representation
        representation["updated_qty"] = instance.trans_qty if instance.trans_qty else 0
        representation["des_stock_id"] = (
            instance.des_stock.id if instance.des_stock else 0
        )
        representation["uom_is_pack"] = (
            instance.stock.uom.is_pack_unit if instance.stock.uom else False
        )
        representation["base_uom_is_pack"] = (
            instance.stock.item.uom.is_pack_unit if instance.stock.item.uom else False
        )

        # Add price-related information to the representation
        representation["price"] = (
            instance.stock.item_price.sales_price if instance.stock.item_price else None
        )

        return representation


class TransferSerializer(serializers.ModelSerializer):
    transfers = TransferItemSerializer(many=True, read_only=True)
    purpose_cd_label = serializers.CharField(
        source="get_purpose_cd_display", read_only=True, required=False
    )

    class Meta:
        model = Transfer
        fields = (
            "id",
            "transfer_no",
            "from_stk",
            "to_stk",
            "trans_dt",
            "purpose_cd",
            "purpose_cd_label",
            "transfers",
            "edited_at",
        )

    def to_representation(self, instance):
        """
        Customize the representation of the serialized Transfer instance.

        This method adds additional information to the serialized Transfer representation,
        such as warehouse names for source and destination stocks.

        Args:
            instance (Transfer): The Transfer instance to be serialized.

        Returns:
            dict: The customized representation of the Transfer instance.
        """
        representation = super().to_representation(instance)

        # Add warehouse names to the representation
        representation["from_stk_warehouse_name"] = (
            instance.from_stk.warehouse_name if instance.from_stk else None
        )
        representation["to_stk_warehouse_name"] = (
            instance.to_stk.warehouse_name if instance.to_stk else None
        )

        return representation
