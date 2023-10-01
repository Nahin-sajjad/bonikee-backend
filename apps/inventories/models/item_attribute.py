from django.db import models
from apps.share.models.base_model import BaseModel
from django.contrib.postgres.fields import ArrayField


class ItemAttribute(BaseModel):

    attribute_name = models.CharField(max_length=264)
    OPTION_CHOICES = [
        ('1', 'Select'),
        ('2', 'Type')
    ]
    attribute_option = models.CharField(choices=OPTION_CHOICES, max_length=128)

    class Meta:
        db_table = "INV_Item_Attribute"

    def __str__(self) -> str:
        return self.attribute_name


class ItemAttributeValue(BaseModel):
    attribute = models.ForeignKey(
        ItemAttribute, related_name='item_attribute', on_delete=models.CASCADE)
    attribute_value = ArrayField(models.CharField(max_length=128))

    class Meta:
        db_table = "INV_Item_Attribute_Value"
