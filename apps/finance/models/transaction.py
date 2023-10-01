from django.db import models
from apps.finance.models.inc_exp_type import IncExpType
from apps.share.models.base_model import BaseModel

try:
    incTypes = list(IncExpType.objects.all().values_list("code", "type"))
except:
    incTypes = []


class Transaction(BaseModel):
    tran_number = models.CharField(max_length=50, blank=True, null=True)
    tran_date = models.DateTimeField(auto_now=True)
    amount = models.FloatField(default=0)

    TYPE = [
        (1001, "Receivable against Sales Invoice"),
        (1002, "Sales Value"),
        (1003, "Sales Return"),
        (1004, "Payable against Purchase Receipt"),
        (1005, "Purchase Value"),
        (1006, "Purchase Return"),
        (1007, "Receivable against Others"),
        (1008, "Collection"),
        (1009, "Payable against Others"),
        (1010, "Pay"),
        (1011, "Salary"),
        (1012, "Utility"),
        (1013, "Rent"),
        (1014, "Advance"),
    ] + incTypes
    tran_type = models.IntegerField(choices=TYPE, blank=True, null=True)

    GROUP = ((102, "Income"), (103, "Expense"), (101, "Receivables"), (104, "Payables"))
    tran_group = models.IntegerField(choices=GROUP)

    HEAD = (
        (1, "Sales"),
        (2, "Purchase"),
        (3, "Customer Dues"),
        (4, "Vendor Dues"),
        (5, "General Income"),
        (6, "General Expense"),
        (7, "Payroll"),
    )
    tran_head = models.IntegerField(choices=HEAD)

    STATUS = ((1, "Open"), (2, "Posted"))
    status = models.IntegerField(choices=STATUS, default=1)

    class Meta:
        db_table = "FM_Transaction"

    def __str__(self) -> str:
        return self.tran_number
