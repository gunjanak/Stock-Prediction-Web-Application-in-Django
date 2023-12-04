from django.urls import path
from .views import nepse_symbols_view,stock_dataFrame_view

urlpatterns = [
    path('symbols/',nepse_symbols_view,name='nepse_symbols'),
    path('stock/',stock_dataFrame_view,name="stock_dataframe"),
]