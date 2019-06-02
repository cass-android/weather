
# coding: utf-8

# In[3]:

import pandas as pd
import requests
import re
# import sqlite3 # might use later
from bs4 import BeautifulSoup as bs
import datetime
import calendar
from dateutil.relativedelta import *
import smtplib
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



# In[19]:

def email_forecast_weather():
    # Emails file from macbook (weatherforecast1988@gmail.com) to work
    
    wforecast_out = prep_forecast_weather()
    wforecast_out.to_csv(os.path.expanduser("~/Desktop/weather_forecast.csv"),index=False) ### CHECK THIS TONIGHT    
    msg = MIMEMultipart()
    filename = "weather_forecast.csv"
    f = open(os.path.expanduser("~/Desktop/weather_forecast.csv"))
    attachment = MIMEText(f.read())
    attachment.add_header('Content-Disposition', 'attachment',  filename=filename)
    msg.attach(attachment)
    server = smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.connect("smtp.gmail.com",465)
    server.login("weatherforecast1988@gmail.com", "yOnsh{QgrB|{")
    server.sendmail("weatherforecast1988@gmail.com", "CHeide@TorontoHydro.com", msg.as_string())
    server.quit()
    return


# In[11]:

def prep_forecast_weather():
    # downloads forecasts
    # downloads historical data for rolling averages (days_behind * 24 = hours in window)
    
    days_behind = 3
    now = datetime.datetime.now()
    startyr = (now + relativedelta(days =- days_behind)).year
    startmt = (now + relativedelta(days =- days_behind)).month
    endyr = now.year
    endmt = now.month
    
    historicals = download_historical_weather(startyr,endyr,startmt,endmt)
    forecast = scrape_forecast_weather()
    days_behind = 3
    now = datetime.date.today()
    start = datetime.datetime.combine((now + relativedelta(days =- days_behind)),datetime.time(0))
    df1=historicals.loc[start:] # since historicals are pulled month-by-month
    
    # Historicals added to same column as forecasts, for calculating rolling averages
    df2 = pd.DataFrame(columns=['Year','Month','Weekday','Day','Hour','Temp C','Dew Point','Relative Humidity'])
    df2['Temp C'] = df1['DB Temp']
    df2['Dew Point'] = df1['Dew Point Temp']
    df2['Relative Humidity'] = df1['Rel Hum (%)']
    df2 = df2.append(forecast, ignore_index=True)
    
    df2['Avg.3Temp']=df2['Temp C'].rolling(window=72).mean().round(1)
    df2['Avg.3DP']=df2['Dew Point'].rolling(window=72).mean().round(1)
    df2['Avg.3RH']=df2['Relative Humidity'].rolling(window=72).mean().round(1)
    df2['Avg.1Temp']=df2['Temp C'].rolling(window=24).mean().round(1)
    df2['Avg.1DP']=df2['Dew Point'].rolling(window=24).mean().round(1)
    df2['Avg.1RH']=df2['Relative Humidity'].rolling(window=24).mean().round(1)

    wforecast_out = df2.iloc[72:]
    return wforecast_out


def scrape_forecast_weather():
# Function returns a dataframe with 10-day ahead 24-h weather forecast, starting day after the current day
# Full URL: https://www.wunderground.com/hourly/ca/toronto/date/2018-9-25?cm_ven=localwx_hour

    days_ahead = 0 # Starting with current day may mess up index of day_out (due to <24 rows). Same-day functionality not required at this time.
    forecast_out = pd.DataFrame() # Will contain 'day_out' for all days in days_ahead 
    
    while days_ahead < 10:    
    
        # Relativedelta calculates the calendar day of n days_ahead:
        now = datetime.datetime.now()
        day = (now + relativedelta(days =+ days_ahead)).day
        month = (now + relativedelta(days =+ days_ahead)).month
        year = (now + relativedelta(days =+ days_ahead)).year
        weekday = (now + relativedelta(days =+ days_ahead)).weekday()

        # Requests gets content from a url for each calendar day in days_ahead:
        url = 'https://www.wunderground.com/hourly/ca/toronto/date/'+str(year)+'-'+str(month)+'-'+str(day)+'?cm_ven=localwx_hour'       
        request = requests.get(url)
        content = request.content
        soup = bs(content,'html.parser') 
        
        # Finds table rows on page, parses and appends to a list:
        table_in = [each for each in soup.find_all('tr') if 'header' not in str(each)]
        table_out = []

        for row_in in table_in:
            row_out = parse_row(row_in)
            table_out.append(row_out)

        # Table_out modified (adds header, converts to dataframe, adds date columns) --> day_out:
        header = list(soup.find_all('tr')[0].stripped_strings)
        day_out = pd.DataFrame(table_out, columns=header)
        day_out.insert(loc = 0, column = "Year", value = (year))
        day_out.insert(loc = 1, column = "Month", value = (month))
        day_out.insert(loc = 2, column = "Day", value = (day))
        day_out.insert(loc = 3, column = "Weekday", value = (weekday))
        #day_out.index.names = ['Hour']

        # Day_out appended to forecast_out
        forecast_out = forecast_out.append(day_out)   
        days_ahead += 1
         

    # Removes non-digit characters:
    forecast_out["Temp."] = forecast_out["Temp."].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Dew Point"] = forecast_out["Dew Point"].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Humidity"] = forecast_out["Humidity"].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Time"] = forecast_out["Time"].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Time"] = forecast_out["Time"].apply(lambda x: int(re.sub("\d\d$","",str(x))))
    
    # Converts F to C
    forecast_out["Temp."] = forecast_out["Temp."].apply(lambda x: round((int(x)-32)*(5/9),1))
    forecast_out["Dew Point"] = forecast_out["Dew Point"].apply(lambda x: round((int(x)-32)*(5/9),1))
    
    # Standardizes with Excel weekday formula (1-7)
    forecast_out["Weekday"] = forecast_out["Weekday"].apply(lambda x:x+1)
    
    # uses old index as 'Hour' and resets index
    # forecast_out['Hour'] = forecast_out.index
    forecast_out.reset_index(inplace=True)
   
    # Drops, renames and re-arranges columns:    
    forecast_out.rename(columns={
        "Humidity": "Relative Humidity", 
        "Temp.": "Temp C"
    },inplace=True)
    
    forecast_out.drop([
        'Conditions',
        'index',
        'Feels Like',
        'Pressure',
        'Precip',
        'Amount',
        'Wind',
        'Cloud Cover'
    ],axis=1,inplace = True)
    
    # Do we need to drop (above) if we're doing this????
    forecast_out = forecast_out[[
        'Year',
        'Month',
        'Weekday',
        'Day',
        'Time',
        'Temp C',
        'Dew Point',
        'Relative Humidity'
    ]]
    
    #forecast_out.to_csv('~/Desktop/weather_forecast.csv')
    
    return forecast_out

def parse_row(row_in):
# Function returns a list containing data as strings, for a single 'row_in'

    cells_in = [text for text in row_in.find_all('td')]
    row_out = []
    
    # Some cells (divs?) contain multiple strings, these are joined so each cell is a single list item in row_out:
    for cell in cells_in:
        strings = cell.stripped_strings
        cell_contents = []
        
        for string in strings:
            cell_contents.append(string)
            
        cell_out = "".join(cell_contents)
        row_out.append(cell_out)
        
    return row_out


# In[8]:

def download_historical_weather(startyr,endyr,startmt,endmt):
   
    df = pd.DataFrame()
    years = list(range(startyr,endyr+1))
    
    for year in years:
        # Starts at startmt for the first year in years, likewise ends at endmt for last year in years
        startmt2 = startmt if year == startyr else 1
        endmt2 = endmt if year == endyr else 12
       
        year_df = pd.DataFrame()
        months = list(range(startmt2,endmt2+1))
        yr = year
        
        for month in months: 
            
            mo = month       
            header = 14 if month >= 4 and year >= 2018 else 13
            mo = month
            station_id = 48549 # stations can be found at http://climate.weather.gc.ca/historical_data/search_historic_data_e.html 

            url = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID='+str(station_id)+'&Year='+str(yr)+'&Month='+str(mo)+'&Day=30&timeframe=1&submit=Download+Data'
            month_df = pd.read_csv(url, header = header)

            # drops 'flag' columns:
            month_df.drop(
                            ['Temp Flag', 
                            'Visibility Flag',
                            'Stn Press Flag',
                            'Hmdx Flag',
                            'Wind Chill Flag', 
                            'Dew Point Temp Flag', 
                            'Rel Hum Flag',
                            'Wind Dir Flag',
                            'Wind Spd Flag'], 
                          axis =1, 
                          inplace = True
                         )
            # renames columns:
            month_df = month_df.rename(index=str, 
                                       columns={
                                           "Date/Time":"DateTime",
                                           "Temp (°C)": "DB Temp",
                                           "Dew Point Temp (°C)":"Dew Point Temp"
                                           
                                           
                                        
            })

            # Sets index to DateTime:
            month_df['DateTime'] = pd.DatetimeIndex(month_df['DateTime'])
            month_df = month_df.set_index('DateTime')

            # appends month to year
            year_df = year_df.append(month_df)

        today = str(datetime.date.today())
        year_df = year_df.loc[(year_df.index < today)]
    
        # appends year to total
        df = df.append(year_df)
        
        # adds Weekday column (used for load forecaster model)
        # weekday = "DateTime".weekday()
        # df.insert(loc = 3, column = 'Weekday', value = 0)
        
    # Saving to .xlsx converts datetimes to strings. Not recommended.
    ### year_df.to_excel(r"C:\Users\cheide\Desktop\weather_station_"+str(station_id)+".xlsx", encoding='utf-8')
    
    #df.to_csv(r"C:\Users\cheide\Desktop\WDout\station"+str(station_id)+"_"+str(startyr)+"-"+str(startmt)+" to "+str(endyr)+"-"+str(endmt)+".csv", encoding='utf-8')
    return df
    
email_forecast_weather()
