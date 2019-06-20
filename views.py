"""
views imports app and models; these don't import views
"""

from flask import render_template, request
from app import app
from models import Historical, Forecast, Station, Current
import datetime

import plotly
import plotly.graph_objs as go 

import pandas as pd
import numpy as np 
import json


@app.route('/')
def index():   

    line = create_plot()
    return render_template("index.html", plot=line)    
    
def create_plot():
    N = 40
    now = datetime.datetime.now()
    x00 = [x.id for x in Historical.query.filter(Historical.id >= now - datetime.timedelta(days=7)).order_by(Historical.id)]
    y00 = [x.drybulb for x in Historical.query.filter(Historical.id >= now - datetime.timedelta(days=7)).order_by(Historical.id)]

    x0 = [x.id for x in Current.query.all()]
    y0 = [x.drybulb for x in Current.query.all()]

    # latest forecast (retrieved hourly)
    # just select the latest 
    
    # x1 = 

    # y1 =   
        
    # retrieved on roughly this hour, 1d ago
    # datetime greater than now minus 1d; less than five minutes after now minus 1d
    
    x2 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=1),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=1435)).order_by(Forecast.id)]

    y2 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=1),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=1435)).order_by(Forecast.id)]

    # retrieved on roughly this hour, 2d ago
    # datetime greater than now minus 2d; less than five minutes after now minus 2d
    
    x3 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=2),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=2875)).order_by(Forecast.id)]

    y3 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=2),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=2875)).order_by(Forecast.id)]

    historicals = go.Scatter(
            x=x00,
            y=y00,
            name='historicals',
            line=dict(
                color = ('rgb(192,192,192)'),
                width = 2,)
            )

    actuals = go.Scatter(
            x=x0,
            y=y0,
            name='actuals',
            mode='lines',
            line=dict(
                color = ('rgb(192,192,192)'),
                width = 2,)
            )
    

    forecasts_1d = go.Scatter(
            x=x2,
            y=y2,
            name='forecasts_1d',
            line=dict(
                color = ('rgb(192,192,192)'),
                width = 2,)
            )

    forecasts_2d = go.Scatter(
            x=x3,
            y=y3,
            name='forecasts_2d',
            line=dict(
                color = ('rgb(192,192,192)'),
                width = 2,)
            )

    data = [historicals, actuals, forecasts_1d, forecasts_2d]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
