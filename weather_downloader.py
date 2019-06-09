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

def download_month(month, year, station = 31688):
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
    month_df = month_df.set_index('datetime')

    # Changes hour to an integer
    # month_df['time'] = pd.to_numeric(month_df['time'].fillna(0), errors='coerce')

    return month_df

def download_year(year,startmt=1,endmt=12): 
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

def add_data(year):
      # Saves to psql db
    engine = create_engine("postgresql://localhost/weather")
    data = download_year(year)
    data.to_sql(name='historicals', con=engine, if_exists='append')
    