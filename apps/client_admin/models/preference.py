from apps.share.models.base_model import BaseModel
from django.db import models


class Preference(BaseModel):
    logo = models.ImageField(blank=True, null=True, upload_to="logo")
    admin = models.JSONField(default=list,blank=True, null=True)
    product = models.JSONField(default=list,blank=True, null=True)
    invoice = models.JSONField(default=list,blank=True, null=True)
    purchase = models.JSONField(default=list,blank=True, null=True)
    finance = models.JSONField(default=list,blank=True, null=True)

    class Meta:
        db_table = "TM_Preference"
