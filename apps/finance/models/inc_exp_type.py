from django.db import models
from apps.share.models.base_model import BaseModel


class IncExpType(BaseModel):
    type = models.CharField(max_length=100)
    code = models.PositiveIntegerField(blank=True, null=True)
    # inc_exp_grp = models.CharField(max_length=1)

    class Meta:
        db_table = 'FM_Inc_Exp_Type'

    def save(self, *args, **kwargs):
        if not self.code:
            # If the code is not set, get the last code value for this user
            last_code = IncExpType.objects.first()
            if last_code:
                self.code = last_code.code + 1
            else:
                # If there are no previous records for this user, set the code to 1101
                self.code = 1101

        super(IncExpType, self).save(*args, **kwargs)
