from django.db import models

# Create your models here.
from apps.share.models.base_model import BaseModel


class Category(BaseModel):
    # id
    category_name = models.CharField(max_length=250)
    descr = models.TextField(
        blank=True,
        null=True,
    )
    category_code = models.CharField(max_length=100)
    cat_parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inv_categories",
    )

    class Meta:
        db_table = "INV_Category"
        unique_together = ("category_name", "tenant")

    def __str__(self) -> str:
        return self.category_name
