from django.contrib import admin

from apps.inventories.models.warehouse import Warehouse
from apps.inventories.models.brand import Brand
from apps.inventories.models.category import Category
from apps.inventories.models.item import Item, ItemLineAtribute
from apps.inventories.models.uom import UOM
from apps.inventories.models.stock import Stock
from apps.inventories.models.production import Production
from apps.inventories.models.transfer import Transfer, TransferItem
from apps.inventories.models.adjust import Adjust
from apps.inventories.models.stock_price import StockPrice
from apps.inventories.models.item_attribute import ItemAttribute, ItemAttributeValue


admin.site.register([Warehouse, Category, UOM, Brand, Item,  Stock, Production, Transfer,
                    Adjust, ItemAttribute, TransferItem, ItemAttributeValue, ItemLineAtribute, StockPrice])
