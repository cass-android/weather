import pandas as pd
import datetime
import requests
import re
from bs4 import BeautifulSoup as bs
from dateutil.relativedelta import *
from sqlalchemy import create_engine
import os
from app import db
from models import Forecast, Current

def add_current():
    session = db.session         # creates a SQLAlchemy Session
    this_hour = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
    
    try:
        row = get_current()
        new_data = Current(
            id=row['id'], 
            drybulb=row['drybulb'], 
            relative_humidity=row['relative_humidity']
            )
        session.merge(new_data) # adds new currents
        
        Current.query.filter(
            Current.id < this_hour - datetime.timedelta(hours=200)
        ).delete()                # deletes old currents
        
        session.commit()       # commits changes to db

    except:
        flash('something messed up')

def add_forecasts():
    session = db.session        # creates a SQLAlchemy Session
        
    try:
        df = get_forecasts()
        for row in df.itertuples(): 
            data = Forecast(
                            id=row[0], 
                            retrieval_time=row[1],
                            drybulb=row[2], 
                            relative_humidity=row[3]
                            )
            session.merge(data) # adds new forecasts

        Forecast.query.filter(
            Forecast.id < this_hour - datetime.timedelta(hours=190)
        ).delete()          # deletes old forecasts
        
        session.commit()    # commits changes to db

    except:
        flash('something messed up')

# current weather
def get_current():
    url = 'http://api.openweathermap.org/data/2.5/weather?id=6167865&APPID=631d59f50ab1841ba7af0f0f706e1505'
    r = requests.get(url, verify=True).json()
    if r:
        row={'id': datetime.datetime.now().replace(microsecond=0,second=0,minute=0),
             'drybulb':r['main']['temp']-272.15,
             'relative_humidity':r['main']['humidity']}
        return row
    else:
        flash('Error!')


def get_forecasts():
    # 5-day 3-h forecast (only free one available)
    url = 'http://api.openweathermap.org/data/2.5/forecast?id=6167865&APPID=631d59f50ab1841ba7af0f0f706e1505'
    response = requests.get(url, verify=True)
    r = response.json()
    
    if response:
        df=pd.DataFrame()
        for dt in r['list']:    
            row={'datetime':dt['dt_txt'],
                 'retrieval_time':datetime.datetime.now().replace(microsecond=0,second=0,minute=0),
                 'drybulb':dt['main']['temp']-273.15,
                 'relative_humidity':dt['main']['humidity']}
            # note: Kelvin to Celcius
            
            df = df.append(row, ignore_index=True)
        df.set_index(pd.DatetimeIndex(df['datetime']), inplace=True)
        return df[['retrieval_time','drybulb', 'relative_humidity']]        

    else:
        flash('Response Error')


