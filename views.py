"""
views imports app and models; these don't import views
"""
# -*- coding: utf-8 -*-

from flask import render_template, request
from app import app
from models import Historical, Forecast, Station, Current
import datetime

import plotly
from plotly import graph_objs as go
from plotly import plotly as py 
from plotly import tools
import matplotlib as mpl

import pandas as pd
import numpy as np 
import json


@app.route('/')
def index():   

    plot = create_plot()
    plot2 = create_plot2()
    return render_template("index.html", plot=plot, plot2=plot2)    
    
def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def create_plot():
    
    # Variables
    w=4
    h=48
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
    data=[]

    # Layout
    layout = go.Layout(
    title=go.layout.Title(
        text='Weather Forecast Tracker',
            font=dict(
                family='Helvetica, monospace',
                size=20
	            )
    ),

    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text='Week of {}'.format((now - datetime.timedelta(days=now.weekday())).date()),
            font=dict(
                family='Helvetica, monospace',
                size=18
            )
        )
    ),

    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='Temperature \u2103',
            font=dict(
                family='Helvetica, monospace',
                size=18
	            )
	        )
	    )
	)

    # actuals
    x0 = [x.id for x in Current.query.filter(Current.id >= now - datetime.timedelta(days=7)).order_by(Current.id)]
    y0 = [x.drybulb for x in Current.query.filter(Current.id >= now - datetime.timedelta(days=7)).order_by(Current.id)]



    actuals = go.Scatter(
        x=x0,
        y=y0,
        name='actual temperature',
        mode='lines',
        line=dict(
            color = ('#FF007F'),
            width = w)
        )   

    data.append(actuals)

    # hourly for past n hours 
    for n in range(1,h):
        x = [x.id for x in Forecast.query.filter(Forecast.retrieval_time >= now - datetime.timedelta(minutes=60*n),
            Forecast.retrieval_time < now - datetime.timedelta(minutes=60*n-10)).order_by(Forecast.id)]

        y = [x.drybulb for x in Forecast.query.filter(Forecast.retrieval_time >= now - datetime.timedelta(minutes=60*n),
            Forecast.retrieval_time < now - datetime.timedelta(minutes=60*n-10)).order_by(Forecast.id)]

        # Colour gradient
        c1='#3399FF' #more distant
        c2='#990099' #nearer
        mix=1-n/h

        if n in (1, h-1):
        	l= True
        else: 
        	l= False

        forecasts = go.Scatter(
                x=x,
                y=y,
                name='forecast {} h ago'.format(n),
                line=dict(
                    color = (colorFader(c1,c2,mix)),
                    width = w*(1/n)**(5/8),
                    ),
                showlegend=l,
                )
        data.append(forecasts)



    data=data[::-1]
    
    fig = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_plot2():
    data=[]
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

    # Layout
    layout = go.Layout(
    title=go.layout.Title(
        text='Weather Forecast Tracker 2',
        font=dict(
                family='Helvetica, monospace',
                size=20
                )
    ),

    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text='Week of {}'.format((now - datetime.timedelta(days=now.weekday())).date()),
            font=dict(
                family='Helvetica, monospace',
                size=18
            )
        )
    ),

    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='Temperature \u2103',
            font=dict(
                family='Helvetica, monospace',
                size=18
	            )
	        )
	    )
	)

    fig = go.Figure(data=data, layout=layout)
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON2



