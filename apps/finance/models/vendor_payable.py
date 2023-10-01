from django.db import models
from apps.vendors.models.vendor import Vendor  # Import the Vendor model
from apps.share.models.base_model import BaseModel


class VendorPayable(BaseModel):
    """
    Model representing payables associated with vendors.

    Attributes:
        vendor (ForeignKey): Reference to the Vendor associated with the payable.
        payable_num (CharField): Payable number or identifier.
        amt (FloatField): Payable amount (default is 0).
        note (TextField): Additional notes or comments about the payable (optional).
        status (CharField): Payable status (optional).

    Meta:
        db_table (str): The database table name for the VendorPayable model.
    """

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vendor_payables",
    )
    payable_num = models.CharField(max_length=100)
    amt = models.FloatField(default=0)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    comitted_payment_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "FM_Vendor_Payable"
