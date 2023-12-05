from django.urls import path
from .views import nepse_symbols_view,stock_dataFrame_view,charts_view

urlpatterns = [
    path('symbols/',nepse_symbols_view,name='nepse_symbols'),
    path('stock/<str:symbol>/',stock_dataFrame_view,name="stock_dataframe"),
    path('chart/',charts_view,name='chart_view'),
]