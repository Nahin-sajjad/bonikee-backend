from django.db.models import Q

from apps.clients.models import TenantUser

import datetime
import random


def validate_tenant_user(tenant, user):
    return TenantUser.objects.filter(Q(tenant=tenant) & Q(user=user)).exists()


def get_tenant_user(self):
    return self.request.user.user_tenant_users.all().first()


def get_primary_warehouse(tenant):
    warehouse_list = tenant.warehouse_base_models.all()
    for warehouse in warehouse_list:
        if warehouse.is_primary:
            return warehouse

    # If no primary warehouse is found, you can return None or raise an exception
    return None


def generate_stock_identity(uom_id, lot_number, per_pack_qty, exp_date):
    stock_identity = (
        f'{uom_id}-{lot_number}-{"{:.2f}".format(float(per_pack_qty))}-{exp_date}'
    )
    return stock_identity


def generate_invoice_number():
    # Get the current date
    current_date = datetime.date.today()

    # Generate a random ID
    id_number = random.randint(10000, 99999)

    # Format the date as desired (e.g., YYYYMMDD)
    formatted_date = current_date.strftime("%Y%m%d")

    # Combine the formatted date and ID to create the invoice number
    invoice_number = f"INV-{formatted_date}-{id_number}"

    return invoice_number


def number_generate(previous_number):
    parts = previous_number.split("-")
    text = parts[0]
    year = int(parts[1])
    count = int(parts[-1])

    current_year = (
        datetime.datetime.now().year
    )  # You can replace this with the actual current year

    if year != current_year:
        year = current_year
        count = 1
    else:
        count += 1

    new_number = f"{text}-{year}-{count}"
    return new_number


def generate_advance_number(previous_number):
    parts = previous_number.split("-")

    new_number = f"{parts[0]}{parts[1]}{parts[-1]}"
    return new_number
