import pandas as pd
import datetime
import requests
import re
from bs4 import BeautifulSoup as bs
from dateutil.relativedelta import *
from sqlalchemy import create_engine
import os
from app import db
from models import Historical, Forecast, Station, Current

def add_current():
    session = db.session     # Creates a SQLAlchemy Session
        
    try:
        row = get_current()
        data = Current(
            id=row['id'], 
            drybulb=row['drybulb'], 
            relative_humidity=row['relative_humidity']
            )
        session.merge(data)
        session.commit()

    except:
        print('something messed up')

def add_historicals(year):
    session = db.session     # Creates a SQLAlchemy Session
        
    try:
        df = get_historicals(year)
        for row in df.itertuples(): 
            data = Historical(
                id=row[0], 
                drybulb=row[1], 
                dewpoint=row[2]
                )
            session.merge(data)
            session.commit()

    except:
        print('something messed up')

def add_forecasts():
    session = db.session     # Creates a SQLAlchemy Session
        
    try:
        df = get_forecasts()
        for row in df.itertuples(): 
            data = Forecast(
                            id=row[0], 
                            retrieval_time=row[1],
                            drybulb=row[2], 
                            relative_humidity=row[3]
                            )
            session.merge(data)
            session.commit()

    except:
        print('something messed up') 

# current weather
def get_current():
    url = 'http://api.openweathermap.org/data/2.5/weather?id=6167865&APPID=631d59f50ab1841ba7af0f0f706e1505'
    r = requests.get(url, verify=True).json()
    if r:
        row={'id': datetime.datetime.now(),
             'drybulb':r['main']['temp']-272.15,
             'relative_humidity':r['main']['humidity']}
        return row
    else:
        print('Error!')

def get_historicals(year,startmt=1,endmt=12): 
    df = pd.DataFrame()     
    year_df = pd.DataFrame()
    yr = year
    
    months = list(range(startmt,endmt+1))
    for month in months:    
        # Downloads month and appends to year
        year_df = year_df.append(download_month(month, year))
     
    # Removes future timestamps (these are in the dataset)
    today = str(datetime.date.today())
    year_df = year_df.loc[(year_df.index < today)]
    return year_df

def get_forecasts():
    # 5-day 3-h forecast (only free one available)
    url = 'http://api.openweathermap.org/data/2.5/forecast?id=6167865&APPID=631d59f50ab1841ba7af0f0f706e1505'
    response = requests.get(url, verify=True)
    r = response.json()
    
    if response:
        df=pd.DataFrame()
        for dt in r['list']:    
            row={'datetime':dt['dt_txt'],
                 'retrieval_time':datetime.datetime.now(),
                 'drybulb':dt['main']['temp']-273.15,
                 'relative_humidity':dt['main']['humidity']}
            # note: Kelvin to Celcius
            
            df = df.append(row, ignore_index=True)
        df.set_index(pd.DatetimeIndex(df['datetime']), inplace=True)
        return df[['retrieval_time','drybulb', 'relative_humidity']]        

    else:
        print('Response Error')


def download_month(month, year, station = 31688):
############################################ government canada hourly historical weather #######################################
############### Downloads hourly weather data from government canada website, for user specified time period ####################

# Example Download url: http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=48549&Year=2018&Month=9&Day=13&timeframe=1&submit=Download+Data
# Example Page url: http://climate.weather.gc.ca/climate_data/hourly_data_e.html?StationID=48549
# Glossary: http://climate.weather.gc.ca/glossary_e.html

# 48549 - Toronto City Centre - missing data?
# 31688 - Toronto City

    yr = year
    m = month
    if month >= 4 and year == 2018:
        header = 14
    elif year > 2018:
        header = 14
    else:
        header = 13
        
    station_id = station # stations can be found at http://climate.weather.gc.ca/historical_data/search_historic_data_e.html 

    url = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID='+str(station_id)+'&Year='+str(yr)+'&Month='+str(m)+'&Day=30&timeframe=1&submit=Download+Data'
    month_df = pd.read_csv(url, header = header)


    # drops 'flag' columns:         
    month_df.drop(
                    [
                    "Year",
                    "Month",
                    "Day",
                    "Time",
                    'Temp Flag', 
                    'Visibility Flag',
                    'Stn Press Flag',
                    'Hmdx Flag',
                    'Wind Chill Flag', 
                    'Dew Point Temp Flag', 
                    'Rel Hum Flag',
                    'Wind Dir Flag',
                    'Wind Spd Flag'
                    ], 
                  axis =1, 
                  inplace = True
                 )
                            
    # renames columns:
    month_df = month_df.rename(index=str, 
                               columns={

                                   "Date/Time":"datetime",
                                   "Temp (°C)": "drybulb",
                                   "Dew Point Temp (°C)":"dewpoint",
                                   "Rel Hum (%)" : "relative_humidity",
                                   "Wind Dir (10s deg)" : "wind_dir_10s_deg",
                                   "Wind Spd (km/h)" : "wind_spd_kmh",
                                   "Visibility (km)" : "visibility_km",
                                   "Stn Press (kPa)" : "stn_press_kpa",
                                   "Hmdx" : "hmdx",
                                   "Wind Chill" : "wind_chill",
                                   "Weather" : "weather"
                                
    })

    # Sets index to DateTime:
    month_df = month_df.set_index(pd.DatetimeIndex(month_df['datetime']))

    # Changes hour to an integer
    # month_df['time'] = pd.to_numeric(month_df['time'].fillna(0), errors='coerce')

    return month_df[[
        'drybulb',
        'dewpoint'
    ]].fillna(0)


   
def scrape_forecast():
    # NOTE: this is no longer working reliably, I think they are blocking me or something. Replaced with 'get_forecast()'
    # Function returns a dataframe with 10-day ahead 24-h weather forecast, starting day after the current day
    # Full URL: https://www.wunderground.com/hourly/ca/toronto/date/2018-9-25?cm_ven=localwx_hour

    days_ahead = 1 
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
        try:
            request = requests.get(url)
        except requests.exceptions.RequestException as e:
            print (e)

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
        day_out.insert(loc = 0, column = "year", value = (year))
        day_out.insert(loc = 1, column = "month", value = (month))
        day_out.insert(loc = 2, column = "day", value = (day))
        day_out.insert(loc = 3, column = "weekday", value = (weekday))
        # day_out.index.names = ['Hour']

        # Day_out appended to forecast_out
        forecast_out = forecast_out.append(day_out)
        days_ahead += 1
         

    # Removes non-digit characters:
    forecast_out["Temp."] = forecast_out["Temp."].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Dew Point"] = forecast_out["Dew Point"].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Humidity"] = forecast_out["Humidity"].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["Time"] = forecast_out["Time"].apply(lambda x: int(re.sub("\D","",str(x))))
    forecast_out["time"] = forecast_out["Time"].apply(lambda x: int(re.sub("\d\d$","",str(x))))
    
    # adds datetime column
    forecast_out['datetime']=pd.to_datetime(forecast_out[['year', 'month', 'day', 'time']]
                            .astype(str).apply(' '.join, 1), format='%Y %m %d %I')
    
    # sets index to datetime
    forecast_out.set_index('datetime', inplace=True)
    
    # Converts F to C
    forecast_out["Temp."] = forecast_out["Temp."].apply(lambda x: round((int(x)-32)*(5/9),1))
    forecast_out["Dew Point"] = forecast_out["Dew Point"].apply(lambda x: round((int(x)-32)*(5/9),1))
    
    # Standardizes with Excel weekday formula (1-7)
    forecast_out["weekday"] = forecast_out["weekday"].apply(lambda x:x+1)
    
   
    # Drops, renames and re-arranges columns:    
    forecast_out.rename(columns={
        "Humidity": "relative_humidity", 
        "Temp.": "drybulb",
        "Dew Point": "dewpoint"

    },inplace=True)
    
    return forecast_out[[
        'drybulb',
        'dewpoint'
    ]].fillna(0)

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
