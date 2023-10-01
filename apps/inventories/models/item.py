from django.db import models

from apps.share.models.base_model import BaseModel

# from .item_type import ItemType
from .brand import Brand
from .category import Category
from .uom import UOM

from apps.share.services.image_delete import storage_image_delete
from apps.share.services.image_process import image_processing


class Item(BaseModel):
    # id
    item_title = models.CharField(max_length=250)
    manufac = models.CharField(max_length=250, blank=True, null=True)
    item_image = models.ImageField(blank=True, null=True)
    sku = models.TextField(blank=True, null=True)

    threshold_qty = models.FloatField(default=0)

    description = models.TextField(blank=True, null=True)  # new

    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inv_items",
    )
    uom = models.ForeignKey(
        UOM, blank=True, null=True, on_delete=models.SET_NULL, related_name="inv_items"
    )
    brand = models.ForeignKey(
        Brand,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inv_items",
    )

    ITEM_CHOICES = [
        ("1", "Raw Material"),
        ("2", "Finished"),
    ]
    item_type_code = models.CharField(
        max_length=250, blank=True, null=True, choices=ITEM_CHOICES
    )

    class Meta:
        db_table = "INV_Item"

    def delete(self, *args, **kwargs):
        # Delete the file associated with the instance
        if self.item_image:
            storage_image_delete(self.item_image.name)
        super(Item, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Item, self).save(*args, **kwargs)

        if self.item_image:
            # Call the image_processing function and update item_image
            image_processing(self.item_image.name)


class ItemLineAtribute(BaseModel):
    item = models.ForeignKey(
        Item,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inv_item_attributes",
    )
    option_name = models.CharField(max_length=100, blank=True, null=True)
    attributes = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        db_table = "INV_ItemLineAtribute"
