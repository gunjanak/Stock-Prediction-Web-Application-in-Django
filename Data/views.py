from django.shortcuts import render
from django.http import JsonResponse

from Data.utlis import nepse_symbols,custom_business_week_mean,stock_dataFrame


# Create your views here.
def nepse_symbols_view(request):
    output = nepse_symbols()
    print(output)
    context = {'stocks':output}

    return JsonResponse(context)

def stock_dataFrame_view(request):
    df = stock_dataFrame("NTC")

    #convert dataframe to a list of dictionaries
    df_dict_list = df.to_dict('records')

    context = {"data":df_dict_list}

    return render(request,"stock_data.html",context)
