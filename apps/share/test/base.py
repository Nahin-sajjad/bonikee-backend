from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import User

from apps.inventories.models.category import Category
from apps.inventories.models.item import Item
from apps.inventories.models.uom import UOM
from apps.inventories.models.brand import Brand
from apps.inventories.models.warehouse import Warehouse
from apps.inventories.models.stock import Stock
from apps.inventories.models.stock_price import StockPrice
from apps.inventories.models.adjust import Adjust
from apps.inventories.models.transfer import Transfer, TransferItem

from apps.vendors.models.vendor import Vendor

from apps.tenants.models.tenant import Tenant
from apps.tenants.models.tenant_user import TenantUser
from apps.procurement.models.receipt import Receipt, ReceiptLineItem
from apps.procurement.models.bill import BillPay, BillPayLineItem
from apps.procurement.models.pur_return import PurReturn, PurReturnLineItem
from apps.finance.models.income import Income
from apps.share.views import number_generate

from apps.sales.models.invoice import Invoice, InvoiceLineItem
from apps.sales.models.challan import Challan, ChallanLineItem

from apps.customers.models import Customer

from apps.hr.models.advance import Advance
from apps.hr.models.attendance import Attendance
from apps.hr.models.department import Department
from apps.hr.models.designation import Designation
from apps.hr.models.employee import Employee
from apps.hr.models.salary import Salary

import io
from PIL import Image
from datetime import datetime


class BaseTestCase(APITestCase):

    def setUp(self):
        self.user = self.create_user_object()
        self.tenant = self.get_or_create_tenant()
        self.tenant_user = self.get_or_create_tenant_user()
        self.client = APIClient()
        self.authenticate_client()

    def authenticate_client(self):
        self.client.force_authenticate(user=self.user)

    def create_user_object(self):
        user = User.objects.create_user(
            email='testuser@email.com',
            password='testpassword',
        )
        return user

    def get_or_create_tenant(self):
        try:
            id = self.tenant.id
        except:
            id = None

        data = {
            "tenant_name": 'Tenant 1',
            "domain_url": 'http://localhost:8000/admin/tenants/tenant/add/',
        }
        tenant, _ = Tenant.objects.get_or_create(id=id, defaults=data)
        return tenant

    def get_or_create_tenant_user(self):
        user = self.user
        tenant = self.tenant
        data = {
            "user_id": user.id,
            "tenant_id": tenant.id,
        }
        tenant_user = TenantUser.objects.get_or_create(id=1, defaults=data)
        return tenant_user

    def get_or_create_category(self, number):
        data = {
            "id": number,
            "category_name": f"category_name_{number}",
            "descr": "descr",
            "short_note": "short_note",
            "tenant": self.tenant
        }
        category, _ = Category.objects.get_or_create(id=number, defaults=data)
        return category

    def get_or_create_brand(self, number):
        data = {
            "id": number,
            "brand_name": f"brand_name_{number}",
            "tenant": self.tenant
        }
        brand, _ = Brand.objects.get_or_create(id=number, defaults=data)
        return brand

    def get_or_create_transfer(self, number):
        data = {
            'from_stk': self.get_or_create_warehouse(number),
            # Here is the culprit
            'to_stk': self.get_or_create_warehouse(number+1),
            'purpose_cd': 1,
        }
        transfer, _ = Transfer.objects.get_or_create(id=number, defaults=data)
        return transfer

    def get_or_create_transfer_item(self, number):
        data = {
            'transfer': self.get_or_create_transfer(number),
            'stock': self.get_or_create_stock(number),
            'trans_qty': number*2,
            'trans_unit': self.get_or_create_uom(number)
        }
        transfer_item, _ = TransferItem.objects.get_or_create(
            id=number, defaults=data)
        return transfer_item

    def get_or_create_uom(self, number):
        data = {
            "id": number,
            "uom_name": f"uom_name_{number}",
            "uom_type_cd": 1,
            "tenant": self.tenant
        }
        uom, _ = UOM.objects.get_or_create(id=number, defaults=data)
        return uom

    def get_or_create_item(self, number):
        data = {
            "item_title": f'title_{number}',
            "description": f'description_{number}',
            "manufac": f'manufac_{number}',
            "item_type_code": f'1_{number}',
            "item_image": self.generate_photo(),
            "sku": f'sku_{number}',
            "threshold_qty": 1,
            "category": self.get_or_create_category(number),
            "uom": self.get_or_create_uom(number),
            "brand": self.get_or_create_brand(number),
            "tenant": self.tenant
        }
        item, _ = Item.objects.get_or_create(id=number, defaults=data)
        return item

    def get_or_create_warehouse(self, number):
        data = {
            "id": number,
            "warehouse_name": f"test warehouse_{number}",
            "warehouse_sn": f"test warehouse_{number}",
            "location": f"Test Gulsion Circle {number}",
            "is_primary": False,
            "tenant": self.tenant
        }
        warehouse, _ = Warehouse.objects.get_or_create(
            id=number, defaults=data)
        return warehouse

    def get_or_create_vendor(self, number):
        data = {
            "id": number,
            "vendor_name": f"test vendor_{number}",
            "phone": "01712345678",
            "address": "Test Gulsion Circle 1",
            "company": "Test Glascutr Company",
            "email": "email@example.com",
            "tenant": self.tenant
        }
        vendor, _ = Vendor.objects.get_or_create(id=number, defaults=data)
        return vendor

    def get_or_create_stock(self, number):
        data = {
            "id": number,
            "lot_number": f"100{number}",
            "per_pack_qty": 1,
            "non_pack_qty": 20,
            "quantity": 500,
            'exp_date': '2023-07-25',
            "source": self.get_or_create_warehouse(number),
            "item": self.get_or_create_item(number),
            "uom": self.get_or_create_uom(number),
            "tenant": self.tenant,
        }
        stock, _ = Stock.objects.get_or_create(id=number, defaults=data)
        return stock

    def get_or_create_adjust(self, number):
        data = {
            "adjust_type_cd": 1,
            "adjust_qty": 100,
            "reason_cd": 1,
            'reason': "test adjust",
            "item": self.get_or_create_item(number),
            "tenant": self.tenant
        }
        adjust, _ = Adjust.objects.get_or_create(id=number, defaults=data)
        return adjust

    def generate_photo(self):
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_file = SimpleUploadedFile(
            "test.png", image_io.getvalue(), content_type="image/png")
        return image_file

    def get_or_create_production(self, number):
        data = {
            "id": number,
            "production_identity": f"test production identity{number}",
            "recvd_date": '2023-07-25',
            "recvd_qty": 15,
            "per_pack_qty": 12,
            "non_pack_qty": 6,
            "cost_per_unit": 650,
            "lot_number": "LOT-420",

            "item": self.get_or_create_item(number),
            "uom": self.get_or_create_uom(number),
            # "recvd_by": self.get_or_create_tenant_user(),
            "recvd_by": self.user,
            "recvd_stock": self.get_or_create_warehouse(number),
            "tenant": self.tenant
        }
        warehouse, _ = Warehouse.objects.get_or_create(
            id=number, defaults=data)
        return warehouse

    def get_or_create_receipt(self, number):
        data = {
            "recpt_num": f"RecptNo-{number}",
            "recpt_dt": "2023-07-05T10:19:04.654035+06:00",
            "status": 1,
            "ref_number": f"REF-{number}",
            "tenant": self.tenant,
            "vendor": self.get_or_create_vendor(number),
            "source": self.get_or_create_warehouse(number),
            "recvd_by": self.user,
        }
        receipt, _ = Receipt.objects.get_or_create(
            id=number, defaults=data)
        return receipt

    def get_or_create_receipt_line_item(self, number):

        data = {
            "lot_number": "Lot-123",
            "exp_date": datetime.strptime("2023-07-10", "%Y-%m-%d").date(),
            "recpt_qty": 10,
            "per_pack_qty": 5,
            "price": 25.99,
            "commi": 0.5,
            "reciept_identity": "Receipt-123",
            "recpt": self.get_or_create_receipt(number),
            "item": self.get_or_create_item(number),
            "unit": self.get_or_create_uom(number),
        }

        receipt_line_item, _ = ReceiptLineItem.objects.get_or_create(
            id=number, defaults=data)
        return receipt_line_item

    def get_or_create_bill_pay(self, number):
        data = {
            'id': number,
            'tenant': self.tenant,
            "recpt": self.get_or_create_receipt(number),
            "status": 2,
            "pay_method": 1,
            "bill_amt": 63920,
            "adv_amt": 63920
        }
        pays_line_items = [
            {
                "recpt_item": 1
            },
            {
                "recpt_item": 2
            },
            {
                "recpt_item": 4
            },
            {
                "recpt_item": 5
            }
        ]

        bill_pay, _ = BillPay.objects.get_or_create(id=number, defaults=data)

        for line_item_data in pays_line_items:
            print(line_item_data["recpt_item"])
            recpt_item_id = line_item_data["recpt_item"]
            recpt_item = self.get_or_create_receipt_line_item(recpt_item_id)

            BillPayLineItem.objects.create(
                bill=bill_pay, recpt_item=recpt_item)

        return bill_pay

    def get_or_create_stock_price(self, number):
        data = {
            "id": number,
            "stock_id": self.get_or_create_stock(number).id,
            "markup": 5,
            "mark_down": 0,
            'sales_price': 200,
            "min_price": 150,
            "tenant": self.tenant
        }
        stock_price, _ = StockPrice.objects.get_or_create(
            id=number, defaults=data)
        return stock_price

    def get_or_create_customer(self, number):
        data = {
            "id": number,
            "tenant": self.tenant,
            "customer_name": f"test customer {number}",
            "phone": 12345678901,
            "email": "test@email.com",
            "address": "test address"
        }

        customer, _ = Customer.objects.get_or_create(id=number, defaults=data)
        return customer

    def get_or_create_invoice(self, number):
        data = {
            "id": number,
            "tenant": self.tenant,
            "inv_num": f"Invoice-{number}",
            "inv_dt": "2023-07-05T10:19:04.654035+06:00",
            "cust": self.get_or_create_customer(number),
            "bill_to": "Test address",
            "warehouse": self.get_or_create_warehouse(number),
            "payment_method": "Cash",
            "status": 1,
            "discount_amount": 20,
            "tax_amount": 10,
            "total_amount": 2100,
            "paid_amount": 1800,
            "due_amount": 300,
        }

        invoice, _ = Invoice.objects.get_or_create(id=number, defaults=data)
        return invoice

    def get_or_create_challan(self, number):
        data = {
            "id": number,
            "tenant": self.tenant,
            "challan_number": f"Challan-{number}",
            "challan_dt": "2023-07-05T10:19:04.654035+06:00",
            "invoice": self.get_or_create_invoice(number)
        }
        challan, _ = Challan.objects.get_or_create(id=number, defaults=data)
        return challan

    def get_or_create_pur_return(self, number):
        previous_number = f'{datetime.now().year}-{0}'
        data = {
            'tenant': self.tenant,
            "recpt": self.get_or_create_receipt(number),
            "return_note": "",
            "return_dt": "07/13/2023",
            "return_amt": 89,
            'return_num':number_generate(previous_number)
        }
        pur_return_line_items = [
                {
                    "return_qty": 1,
                    "recpt_item": 1,
                }
            ]
        
        pur_return, _ = PurReturn.objects.get_or_create(id=number, defaults=data)
        
        income_data = {
            'tenant': self.tenant,
            'inc_type_cd': 'Return',
            'amt': pur_return.return_amt,
            'pay_method': 1,
            'note': pur_return.return_note,
            'ref' : pur_return.return_num,
            'paid_by': 'vendor_name'
        }
        
        income, _ = Income.objects.get_or_create(id=number, defaults=income_data)

        for line_item_data in pur_return_line_items:
            recpt_item_id = line_item_data["recpt_item"]
            recpt_item = self.get_or_create_receipt_line_item(recpt_item_id)

            PurReturnLineItem.objects.create(
                pur_retrn=pur_return, recpt_item=recpt_item, return_qty=line_item_data['return_qty'])

        return pur_return
    
    def get_or_create_pur_return_line_item(self, number):
        data = {
            'return_qty': 20,
            'pur_retrn': self.get_or_create_pur_return(1),
            'recpt_item': self.get_or_create_receipt_line_item(1),
        }
        
        pur_return_line_item, _ =PurReturnLineItem.objects.get_or_create(id = number, defaults=data)
        
        return pur_return_line_item
    
    def get_or_create_department(self,number):
        data = {
            'tenant': self.tenant,
            'name': 'Software Development Department'
        }
        department, _ = Department.objects.get_or_create(id = number, defaults=data)
        return department
    
    def get_or_create_designation(self,number):
        data = {
            'tenant': self.tenant,
            'name': 'Junior Software Engineer'
        }
        designation, _ = Designation.objects.get_or_create(id = number, defaults=data)
        return designation

    def get_or_create_employee(self, number):
        data ={
            'tenant': self.tenant,
            "name": "Something{number}",
            "dept": self.get_or_create_department(number),
            "desig": self.get_or_create_designation(number),
            "doj": "2023-07-01",
            "emp_wage_type": 1,
            "hr_per_day": "3",
            "salary": 6000,
            "status": 1,
            "photo": self.generate_photo(),
            "addr": "adasdasd",
            "nid": 3242432423423,
            "phone": "01846445294",
        }
        
        employee ,_ = Employee.objects.get_or_create(id = number, defaults=data)
        
        return employee