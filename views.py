"""
views imports app and models; these don't import views
"""

from flask import render_template, request
from app import app
from models import Historical, Forecast, Station, Current
import datetime

import plotly
from plotly import graph_objs as go
from plotly import plotly as py 

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

    # actuals
    x0 = [x.id for x in Current.query.filter(Current.id >= now - datetime.timedelta(days=7)).order_by(Current.id)]
    y0 = [x.drybulb for x in Current.query.filter(Current.id >= now - datetime.timedelta(days=7)).order_by(Current.id)]

    # latest forecast (retrieved within the last hour)   
    x1 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time >= now - datetime.timedelta(hours=1))
          .order_by(Forecast.id)]

    y1 = [x.drybulb for x in Forecast.query.filter(Forecast.retrieval_time >= now - datetime.timedelta(hours=1))
          .order_by(Forecast.id)]  
        
    # retrieved on roughly this hour, 1d ago
    # datetime greater than now minus 1d; less than five minutes after now minus 1d   
    x2 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=1),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=1435)).order_by(Forecast.id)]

    y2 = [x.drybulb for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=1),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=1435)).order_by(Forecast.id)]

    # retrieved on roughly this hour, 2d ago
    # datetime greater than now minus 2d; less than five minutes after now minus 2d   
    x3 = [x.id for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=2),
        Forecast.retrieval_time < now - datetime.timedelta(minutes=2875)).order_by(Forecast.id)]

    y3 = [x.drybulb for x in Forecast.query.filter(Forecast.retrieval_time > now - datetime.timedelta(days=2),
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
                color = ('rgb(10,128,0)'),
                width = 2,)
            )
    
    forecasts_0d = go.Scatter(
            x=x1,
            y=y1,
            name='forecasts_0d',
            line=dict(
                color = ('rgb(0,51,102)'),
                width = 2,)
            )

    forecasts_1d = go.Scatter(
            x=x2,
            y=y2,
            name='forecasts_1d',
            line=dict(
                color = ('rgb(0,76,153)'),
                width = 2,)
            )

    forecasts_2d = go.Scatter(
            x=x3,
            y=y3,
            name='forecasts_2d',
            line=dict(
                color = ('rgb(0,102,204)'),
                width = 2,)
            )

    data = [historicals, actuals, forecasts_0d, forecasts_1d, forecasts_2d]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    layout = go.Layout(
    title=go.layout.Title(
        text='Weather Forecast Accuracy Tracker',
        xref='paper',
        x=0
    ),
    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text='Degrees C',
            font=dict(
                family='Helvetica, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    ),
    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='Date',
            font=dict(
                family='Helvetica, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )
)
    fig = go.Figure(data=data, layout=layout)

#    return graphJSON
    return graphJSON
