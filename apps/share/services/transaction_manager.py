from apps.finance.models.transaction import Transaction


class TransactionManager:
    def __init__(self, tran_number: str, tenant: str) -> str:
        self.tenant = tenant
        self.tran_number = tran_number

    def transaction_obj(self, tran_group, amount, tran_type, tran_head):
        obj = {
            "tenant": self.tenant,
            "tran_number": self.tran_number,
            "tran_group": tran_group,
            "amount": amount,
            "tran_type": tran_type,
            "tran_head": tran_head,
        }
        return obj

    def transaction_create_or_update(self, tran_group, amount, tran_type, tran_head):
        obj = self.transaction_obj(tran_group, amount, tran_type, tran_head)
        transaction, created = Transaction.objects.update_or_create(
            tran_number=self.tran_number, defaults=obj)

        if created:
            print("New Transaction Created")

        return transaction
