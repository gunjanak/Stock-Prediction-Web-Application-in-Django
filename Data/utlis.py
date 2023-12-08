#this file will scrape merolagani site and scrape the symbols of all the stocks listed in NEPSE
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import talib as ta
import json


import pandas as pd
from datetime import datetime, timedelta


#opening the annapurna express

def nepse_symbols():
    path = 'https://merolagani.com/LatestMarket.aspx'
    r = requests.get(path,headers={'User-Agent': 'Chrome/108.0.0.0'})
    print(r.status_code)
    #Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36

    #creating a beautiful soup object
    bs = BeautifulSoup(r.content,'html.parser')
    tables = bs.find_all('table',attrs={'class': 'table table-hover live-trading sortable'})
    clean_string = re.sub('[0-9.]', '', tables[0].text)
    lines =clean_string.split('\n')


    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    # Extract the alphabets between '\n' and '\n' and store them in a list
    results = [line.strip() for line in lines[1:]]
    modified_list = [element.replace('-', '') for element in results]
    stock_symbols = [element.replace(',','') for element in modified_list]

    return stock_symbols



def custom_business_week_mean(values):
    # Filter out Saturdays
    working_days = values[values.index.dayofweek != 5]
    return working_days.mean()

#function to read stock data from Nepalipaisa.com api
def stock_dataFrame(stock_symbol,start_date='2023-01-01',weekly=False):
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


  return df

def OBV(company_df):
  length = len(company_df)
  #print(length)
  OBV = 0
  obv_daily = []
  for i in range(length-1):
    if(company_df['Close'][i+1] > company_df['Close'][i]):
      OBV = OBV + company_df['Volume'][i+1] 
      obv_daily.append(OBV)
    elif (company_df['Close'][i+1] < company_df['Close'][i]):
      OBV = OBV - company_df['Volume'][i+1] 
      obv_daily.append(OBV)
    else:
      OBV = OBV
      obv_daily.append(OBV)
  company_df2 = company_df
  # Drop first row
  company_df2.drop(index=company_df2.index[0], 
        axis=0, 
        inplace=True)
  
  company_df2['OBV'] = obv_daily
  df_obv = company_df2[['OBV']]
  # print(df_obv)
  obv = df_obv.values
  obv = list(df_obv.values)
  obv = [item.item() for array in obv for item in array]
  # print(obv)
  # print(type(obv[0]))
  #print(len(company_df2))
  return obv


def MACD(company_df):
  macd, macdsignal, macdhist = ta.MACD(company_df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

  # print(macdhist.values)
  company_df['MACD'] = macd
  company_df['MACD_signal'] = macdsignal
  company_df['MACD_hist'] = macdhist
  company_df2 = company_df.dropna()

  mach_hist_df = company_df2[['MACD_hist']]
  mach_hist_df = mach_hist_df.reset_index()
  mach_hist_df['timestamp'] = pd.to_datetime(mach_hist_df['Date'])
  mach_hist_df['Date'] = mach_hist_df['timestamp'].dt.date
  mach_hist_df = mach_hist_df[['Date','MACD_hist']]

  # Macd main line
  macd_main = list(company_df2['MACD'].values)
  # print(macd_main)

  #MACD signal line
  macd_signal_line = list(company_df2['MACD_signal'].values)


  # print(mach_hist_df)
  date = list(mach_hist_df['Date'].values)
  macd_hist = list(mach_hist_df['MACD_hist'].values)
  # print(macd_hist)

  MACD_main_dic = {
     "title":"MACD",
     "data":{
        "labels":date,
        "datasets":[{
           "label":"macd_main",
           "data":macd_main,
           "type":"line"
        },
        {
           "label":"macd_hist",
            "data":macd_hist,
            "type":"bar"
        },
        {
            "label":"macd_hist",
            "data":macd_signal_line,
            "type":"line"
           
        }]
     }
  }


  

  return MACD_main_dic



def processData(dataFrame,frequency):
  if frequency == "weekly":
    print("Weekly data**********************************")
    df = dataFrame.resample('W-FRI').mean()
  else:
    df = dataFrame

  df = df.dropna()
  # df = df.head()
  df = df.reset_index()
  df['timestamp'] = pd.to_datetime(df['Date'])
  df['Date'] = df['timestamp'].dt.date
  date = list(df['Date'].values)
  df.drop('timestamp', axis=1, inplace=True)

  new_df = df.iloc[:, 1:] 

  # print(new_df)
  print("***************date**********************")
  print(date)


  list_of_dicts = new_df.to_dict(orient='list')
  # Create the final list of dictionaries with the desired format
  final_list_of_dicts = [{"label": column, "data": values}
                          for column, values in list_of_dicts.items()]
  main_data = {
        "title":"Stock Price",
        "data":{
            "labels":date,
            "datasets":final_list_of_dicts
        }
    }
  
  # Convert date objects to string representations
  main_data['data']['labels'] = [str(d) for d in main_data['data']['labels']]

  # Convert data to a JSON-formatted string
  chart_data_json = json.dumps(main_data)
  # print(main_data)

  return main_data
   