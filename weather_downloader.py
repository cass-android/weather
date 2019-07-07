import pandas as pd
import datetime
import requests
from dateutil.relativedelta import *
from sqlalchemy import create_engine
from flask import flash
import os
from app import db
from models import Forecast, Current


def get_current():
# current weather conditions
    url = 'http://api.openweathermap.org/data/2.5/weather?id=6167865&APPID=631d59f50ab1841ba7af0f0f706e1505'
    r = requests.get(url, verify=True).json()
    if r:
        row={'id': datetime.datetime.now().replace(microsecond=0,second=0,minute=0),
             'drybulb':r['main']['temp']-272.15, # Kelvin to Celcius
             'relative_humidity':r['main']['humidity']}
        return row
    else:
        print('Unable to get current!')

def add_current():
    session = db.session         # creates a SQLAlchemy Session
    this_hour = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

    row = get_current()
    try:
        new_data = Current(
            id=row['id'], 
            drybulb=row['drybulb'], 
            relative_humidity=row['relative_humidity']
            )
        session.merge(new_data) # adds new currents
 
        Current.query.filter(
            Current.id < this_hour - datetime.timedelta(hours=200)
        ).delete()                # deletes old currents   

    except:
        print('Unable to merge new data')  
    try:    
        session.commit()       # commits changes to db
    except:
        print('Unable to commit session!')

def add_forecasts():
# 5-day 3-h forecast (free)
    url = 'http://api.openweathermap.org/data/2.5/forecast?id=6167865&APPID=631d59f50ab1841ba7af0f0f706e1505'
    response = requests.get(url, verify=True)
    
    if response:
        r = response.json()
        session = db.session        # creates a SQLAlchemy Session
        this_hour = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

        Forecast.query.filter(
            Forecast.id < this_hour - datetime.timedelta(hours=100)
        ).delete()          # deletes old forecasts               

        for dt in r['list']:    
            data=Forecast(
                  id=dt['dt_txt'],
                  retrieval_time=datetime.datetime.now().replace(microsecond=0,second=0,minute=0),
                  drybulb=dt['main']['temp']-273.15, # Kelvin to Celcius
                  relative_humidity=dt['main']['humidity']
            )
            session.merge(data) # adds new forecasts
            
 
        session.commit() 

    else:
        print('Unable to add forecasts!')







