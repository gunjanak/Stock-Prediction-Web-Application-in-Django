from django.urls import path
from .views import (nepse_symbols_view,stock_dataFrame_view,
                    charts_view,candlestick_view,forecast_view)

urlpatterns = [
    path('symbols/',nepse_symbols_view,name='nepse_symbols'),
    path('stock/<str:symbol>/',stock_dataFrame_view,name="stock_dataframe"),
    path('chart/',charts_view,name='chart_view'),
    path('candle/',candlestick_view,name="candle_view"),
    path("forecast/",forecast_view,name="forecast_view")
]