from django.db import models
from apps.vendors.models.vendor import Vendor  # Import the Vendor model
from apps.share.models.base_model import BaseModel


class VendorPay(BaseModel):
    """
    Model representing payments made to vendors.

    Attributes:
        vendor (ForeignKey): Reference to the Vendor associated with the payment.
        pay_num (CharField): Payment number or identifier.
        amt (FloatField): Payment amount (default is 0).
        note (TextField): Additional notes or comments about the payment (optional).
        status (CharField): Payment status (optional).

    Meta:
        db_table (str): The database table name for the VendorPay model.
    """

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vendor_pays",
    )
    pay_num = models.CharField(max_length=100)
    amt = models.FloatField(default=0)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "FM_Vendor_Pay"
