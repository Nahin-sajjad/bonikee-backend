from django.db import models
from apps.share.models.base_model import BaseModel

class Department(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True)
    
