#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import datetime
from sqlalchemy import create_engine

############################################ government canada hourly historical weather #######################################
############### Downloads hourly weather data from government canada website, for user specified time period ####################

# Example Download url: http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=48549&Year=2018&Month=9&Day=13&timeframe=1&submit=Download+Data
# Example Page url: http://climate.weather.gc.ca/climate_data/hourly_data_e.html?StationID=48549
# Glossary: http://climate.weather.gc.ca/glossary_e.html

# 48549 - Toronto City Centre - missing data?
# 31688 - Toronto City


def download_data(startyr,endyr,startmt,endmt):
   
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
            station_id = 31688 # stations can be found at http://climate.weather.gc.ca/historical_data/search_historic_data_e.html 

            url = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID='+str(station_id)+'&Year='+str(yr)+'&Month='+str(mo)+'&Day=30&timeframe=1&submit=Download+Data'
            month_df = pd.read_csv(url, header = header)

            # drops 'flag' columns:
            month_df.drop(
                            [
                            'Year',
                            'Month',
                            'Day',
                            'Time',                            
                            'Temp Flag', 
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
            month_df = month_df.set_index('datetime')

            # appends month to year
            year_df = year_df.append(month_df)

        today = str(datetime.date.today())
        year_df = year_df.loc[(year_df.index < today)]
    
        # appends year to total
        df = df.append(year_df)
        
        # adds Weekday column (used for load forecaster model)
        # weekday = "DateTime".weekday()
        # df.insert(loc = 3, column = 'Weekday', value = 0)
        
    return df

df = download_data(2018,2018,1,12)

engine = create_engine("postgresql://localhost/weather")
df.to_sql('historicals', engine, if_exists='append')


