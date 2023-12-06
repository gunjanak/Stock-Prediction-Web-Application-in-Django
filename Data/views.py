import pandas as pd

from django.shortcuts import render
from django.http import JsonResponse

from Data.utlis import nepse_symbols,custom_business_week_mean,stock_dataFrame,OBV,MACD


# Create your views here.
def nepse_symbols_view(request):
    output = nepse_symbols()
    # print(output)
    context = {'stocks':output}

    return JsonResponse(context)

def stock_dataFrame_view(request,symbol):
    df = stock_dataFrame(symbol)
    print("**************************************************")
    # df = df.head(100)
    print(df)

    #the df with OBV
    
    obv = OBV(df)

    #MACD
    MACD_data = MACD(df) 
    # print(macd_df)


    df = df.reset_index()
    
    df['timestamp'] = pd.to_datetime(df['Date'])
    df['Date'] = df['timestamp'].dt.date
    df = df[['Date','Close','Open','High',"Low"]]
    date = list(df['Date'].values)
    new_df = df.iloc[:, 1:] 
    # print(new_df)
    # Convert DataFrame to a list of dictionaries
    list_of_dicts = new_df.to_dict(orient='list')

    # Create the final list of dictionaries with the desired format
    final_list_of_dicts = [{"label": column, "data": values} for column, values in list_of_dicts.items()]

    # Display the final list of dictionaries
    # print(final_list_of_dicts)



    main_data = {
        "title":"Stock Price",
        "data":{
            "labels":date,
            "datasets":final_list_of_dicts
        }
    }

    OBV_data = {
        "title":"On Balance Volume",
        "data":{
            "labels":date,
            "datasets":[{
                "label":"OBV",
                "data":obv,
                "type":"line"


            }
                
            ]
        }
        
    }
    
    context = {
        "main_data":main_data,
        "obv":OBV_data,
        "macd":MACD_data
    }

    # print(context)

    return JsonResponse(context)


def charts_view(request):
    return render(request,"charts.html")