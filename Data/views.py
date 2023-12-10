import pandas as pd

from django.shortcuts import render
from django.http import JsonResponse

from Data.utlis import (nepse_symbols,custom_business_week_mean,
                        stock_dataFrame,OBV,MACD,processData)
from Data.forecast import (data_for_model,Model_CNN_BGRU,model_prediction,MAPE,final_prediction,stock_dataFrame2)

from Data.forms import ForecastForm,cnnBgruForm

# Create your views here.
def nepse_symbols_view(request):
    output = nepse_symbols()
    # print(output)
    context = {'stocks':output}

    return JsonResponse(context)

def stock_dataFrame_view(request,symbol):
    df = stock_dataFrame(symbol)
    print("**************************************************")
    df = df.head(5)
    # print(df)

    #the df with OBV
    
    obv = OBV(df)

    #MACD
    MACD_data = MACD(df) 
    # print(macd_df)


    df = df.reset_index()
    
    df['timestamp'] = pd.to_datetime(df['Date'])
    df['Date'] = df['timestamp'].dt.date
    df = df[['Date','Close','Open','High',"Low"]]
    # print(df)

    #Transforming data suitable for candlestick chart
    transformed_data = {
    'dataPoints': [
        {'x': date.strftime('%Y-%m-%d'), 'y': [row.Open, row.High, row.Low, row.Close]}
        for date, row in zip(df['Date'], df.itertuples(index=False))
    ]
    }

    # print(transformed_data)



    date = list(df['Date'].values)
    new_df = df.iloc[:, 1:] 
    # print(new_df)
    # Convert DataFrame to a list of dictionaries
    list_of_dicts = new_df.to_dict(orient='list')

    # Create the final list of dictionaries with the desired format
    final_list_of_dicts = [{"label": column, "data": values} for column, values in list_of_dicts.items()]

    # Display the final list of dictionaries
    # print(final_list_of_dicts)
    # print("***************date**********************")
    # print(date)



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
        "macd":MACD_data,
        "candlestick":transformed_data
    }

    # print(context)

    return JsonResponse(context)


def charts_view(request):
    return render(request,"charts.html")

def candlestick_view(request):
    return render(request,"candlestick.html")

def forecast_view(request):

    #this gives list of all the symbols
    output = nepse_symbols()

    #this gives list of all the columns
    df = stock_dataFrame('ADBL')
    df = df.head()
    cols = list(df.columns)
    
    frequency = ["daily","weekly"]

    data_to_chart = None


    if request.method == "POST":
        form = ForecastForm(request.POST,symbols=output,columns=cols,frequency=frequency)
        if form.is_valid():
            selected_symbol = form.cleaned_data['symbol_dropdown']
            selected_column = form.cleaned_data['column_dropdown']
            selected_freq = form.cleaned_data['frequency_dropdown']

            df = stock_dataFrame(selected_symbol)
            df = df[[selected_column]]
            data_to_chart = processData(df,selected_freq)
            # print(data_to_chart)
            



    else:
        form = ForecastForm(symbols=output,columns=cols,frequency=frequency)




    context = {
        "symbols":output,
        "columns":cols,
        "form":form,
        "chartData":data_to_chart,
    }
    # print(context)

    return render(request,"forecast.html",context)





def cnn_bgru_view(request):
    output = nepse_symbols()
    error = None
    prediction = None

    if request.method == "POST":
        form = cnnBgruForm(request.POST,symbols=output)
        if form.is_valid():
            selected_symbol = form.cleaned_data['symbol_dropdown']
            # selected_freq = form.cleaned_data['frequency_dropdown']

            df = stock_dataFrame2(selected_symbol)
            print(df)
            data = data_for_model(df)
            X = data[1]
            Y = data[2]
            model_CNN_BGRU = Model_CNN_BGRU(X,Y,Look_back_period=5)
            record = model_prediction(data,model_CNN_BGRU,
                                      df,Look_back_period=5,future=0)
            record = record.set_index('Date')
            error = MAPE(record)
            error = round(error, 3)
            print("*******************Error********************")
            print(error)
            error = f"{error*100}  %"
            lookback = 5
            prediction = final_prediction(df,lookback,data,model_CNN_BGRU)
            prediction = prediction[0][0]
            print("***********Prediction*******************")
            print(prediction)
            

    else:
        form = cnnBgruForm(symbols=output)
    
    context = {
        "symbols":output,
        "form":form,
        "error":error,
        "prediction":prediction,
    }
    
    
    return render(request,"cnn_bgru.html",context)





