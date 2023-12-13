from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn import preprocessing

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM, Bidirectional, GRU, Conv1D,Conv2D,MaxPooling1D



def custom_business_week_mean(values):
    # Filter out Saturdays
    working_days = values[values.index.dayofweek != 5]
    return working_days.mean()

#function to read stock data from Nepalipaisa.com api
def stock_dataFrame2(stock_symbol,start_date='2023-05-01',weekly=False):
  """
  input : stock_symbol
            start_data set default at '2020-01-01'
            weekly set default at False 
  output : dataframe of daily or weekly transactions
  """
  #print(end_date)
  today = datetime.today()
  # Calculate yesterday's date
  yesterday = today - timedelta(days=1)

  # Format yesterday's date
  formatted_yesterday = yesterday.strftime('%Y-%-m-%-d')
  print(formatted_yesterday)


  path = f'https://www.nepalipaisa.com/api/GetStockHistory?stockSymbol={stock_symbol}&fromDate={start_date}&toDate={formatted_yesterday}&pageNo=1&itemsPerPage=10000&pagePerDisplay=5&_=1686723457806'
  df = pd.read_json(path)
  theList = df['result'][0]
  df = pd.DataFrame(theList)
  #reversing the dataframe
  df = df[::-1]

  #removing 00:00:00 time
  #print(type(df['tradeDate'][0]))
  df['Date'] = pd.to_datetime(df['tradeDateString'])

  #put date as index and remove redundant date columns
  df.set_index('Date', inplace=True)
  columns_to_remove = ['tradeDate', 'tradeDateString','sn']
  df = df.drop(columns=columns_to_remove)

  new_column_names = {'maxPrice': 'High', 'minPrice': 'Low', 'closingPrice': 'Close','volume':'Volume','previousClosing':"Open"}
  df = df.rename(columns=new_column_names)

  if(weekly == True):
    weekly_df = df.resample('W').apply(custom_business_week_mean)
    df = weekly_df

  df = df[['Close']]  
    



  return df


def make_frame(input_frame,scaled_frame,rows,columns):
  for j in range(rows):
    count = 0
    for i in range(0+j,columns+j):
      input_frame[j][count] = scaled_frame[i][0]
      count = count+1
  return input_frame


def data_for_model(company_df,Look_back_period=5,future=0):
  company_df = company_df.fillna(method='ffill')
  numpy_array = company_df.values
  close_array = numpy_array
  entries_total = close_array.shape[0]
  mean_std_array = np.array([close_array.mean(),close_array.std()])
  mean_std_scaler = preprocessing.StandardScaler()
  close_scaled = mean_std_scaler.fit_transform(close_array)
  rows = Look_back_period
  columns = entries_total - (rows+future)
  company_input = np.zeros(shape=(rows,columns))
  company_input = make_frame(company_input,close_scaled,rows,columns)
  company_input = company_input.T
  company_output = np.zeros(shape=(columns,1))
  for i in range(rows,(columns+rows)):
    company_output[i-rows][0] = close_scaled[i+future][0]

  #combiniing all arrays
  features = 1
  company_input_3d = np.zeros(shape=(columns,rows,features))
  company_input_3d[:,:,0] = company_input
  return_list = []
  return_list.append(mean_std_array)
  return_list.append(company_input_3d)
  return_list.append(company_output)

  return return_list


def Model_CNN_BGRU(X,Y,Look_back_period):
  model = Sequential()
  model.add(Conv1D(100,(3),activation='relu',padding='same',input_shape=(Look_back_period,1)))
  model.add(MaxPooling1D(pool_size=2,strides=1,padding='valid'))
  model.add(Bidirectional(GRU(50)))
  model.add(Dense(1))
  model.compile(loss='mean_squared_error',optimizer='adam',metrics=['accuracy'])
  model.fit(X,Y,epochs=100,batch_size=64,verbose=0)
  model_cnn_bgru = model

  return model_cnn_bgru

def model_prediction(data,model,company_df,Look_back_period,future):
  L = Look_back_period
  f = future
  a = data
  mean_std = a[0]
  mean = mean_std[0]
  std = mean_std[1]
  ran = company_df.shape[0]-(L+f)
  company_df = company_df.reset_index()
  

  column_names = ["Date","Actual","Prediction"]
  record = pd.DataFrame(columns=column_names)
 

  for i in range(ran):
    count = i+L
    tail = company_df[i:count]
    tail = tail.set_index('Date')
    numpy_array = tail.values
    predict_input = np.zeros(shape=(1,L,1))
    # print("*******************tail********************")
    # print(tail)
    

    for i in range(L):
      predict_input[:,i] = numpy_array[i]

    predict_scaled = (predict_input-mean)/(std)
    # print("Shape of predict scaled")
    # print(predict_scaled.shape)
    prediction = model.predict(predict_scaled)
    predict_final = (prediction*(std)) + mean

    count = count +f
    date = company_df['Date'][count]
    actual = company_df['Close'][count]
    list_predict = [date,actual,predict_final[0][0]]
    series_predict = pd.Series(list_predict,index=record.columns)
    record = pd.concat([record, pd.DataFrame([series_predict])], ignore_index=True)
    # record = record.append(series_predict,ignore_index=True)
    record['Date'] = pd.to_datetime(record['Date'],infer_datetime_format=True)
   

  return record


def MAPE(record):
  num = record.shape[0]
  record['error'] = abs((record['Actual']-record['Prediction'])/record['Actual'])
  sum2 = record['error'].sum()
  MAPE = sum2/num
  return MAPE

def final_prediction(company_df,lookback,data,model):
  mean_std = data[0]
  mean = mean_std[0]
  std = mean_std[1]

  last_data = company_df.tail(lookback)
  last_data = last_data.values
  predict_scaled = (last_data-mean)/(std)
  predict_scaled = predict_scaled.reshape((1,lookback,1))
  prediction = model.predict(predict_scaled)
  predict_final = (prediction*(std))+mean
  return predict_final





  







    