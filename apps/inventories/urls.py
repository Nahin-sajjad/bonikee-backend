# Base Import
from django.urls import path

# Brand Import
from apps.inventories.views.brand import BrandView, BrandDetailsView
# Category Import
from apps.inventories.views.category import CategoryView, CategoryDetailsView
# Item Import
from apps.inventories.views.item import ItemView, ItemDetailsView
# UOM Import
from apps.inventories.views.uom import UomView, UomDetailsView
# Warehouse Import
from apps.inventories.views.warehouse import WarehouseView, WarehouseDetailsView
# Transfer Import
from apps.inventories.views.transfer import TransferView, TransferDetailsView
# Stock Import
from apps.inventories.views.stock import StockView, WarehouseStockView
from apps.inventories.views.production import ProductionView, ProductionDetailsView
# Adjust Import
from apps.inventories.views.adjust import AdjustView

# Stock Price Import
from apps.inventories.views.stock_price import StockPriceView
from apps.inventories.views.stock_price import StockPriceDetailsView

from apps.inventories.views.item_attribute import ItemAttributeView, ItemAttributeDetailsView
from apps.inventories.views.item_attribute import ItemAttributeValueView, ItemAttributeValueDetailsView

urlpatterns = [
    # Warehouse Urls
    path("warehouse/", WarehouseView.as_view(), name="warehouse"),
    path("warehouse/<int:pk>/", WarehouseDetailsView.as_view(),
         name="warehouse-details"),

    # Category Urls
    path("category/", CategoryView.as_view(), name="categories"),
    path("category/<int:pk>/", CategoryDetailsView.as_view(),
         name="category-details"),

    # Brand Urls
    path("brand/<int:pk>/", BrandDetailsView.as_view()),
    path("brand/", BrandView.as_view()),

    # Item Urls
    path("item/", ItemView.as_view(), name="item"),
    path("item/<int:pk>/", ItemDetailsView.as_view(), name="item-details"),

    # UOM Urls
    path("uom/<int:pk>/", UomDetailsView.as_view()),
    path("uom/", UomView.as_view()),

    # UOM Urls
    path("transfer/<int:pk>/", TransferDetailsView.as_view(),
         name='transfer-details'),
    path("transfer/", TransferView.as_view(), name="transfer-list"),

    # Stock Urls
    # path("stock/<int:pk>/", UomDetailsView.as_view()),
    path("stock/", StockView.as_view(), name='stock'),  # StockView 1

    path("production/", ProductionView.as_view(), name='productions'),
    path("production/<int:pk>/", ProductionDetailsView.as_view(),
         name='production-details'),

    path("warehouse/stock/<int:pk>/", WarehouseStockView.as_view()),  # StockView 2

    # Adjust Urls
    # path("adjust/<int:pk>/", UomDetailsView.as_view()),
    path("adjust/", AdjustView.as_view(), name="adjust"),

    # Stock Price Urls
    path("stock/price/", StockPriceView.as_view(), name="stock_price"),
    path("stock/price/<int:pk>/", StockPriceDetailsView.as_view(),
         name="stock_price_details"),


    # ItemAttribute Urls
    path("item-attribute/", ItemAttributeView.as_view(), name="item_attribute"),
    path("item-attribute/<int:pk>/", ItemAttributeDetailsView.as_view(),
         name="item_attribute_details"),

    # ItemAttribute Urls
    path("item-attribute-value/", ItemAttributeValueView.as_view(),
         name="item_attribute_value"),
    path("item-attribute-value/<int:pk>/", ItemAttributeValueDetailsView.as_view(),
         name="item_attribute_value_details"),
]
