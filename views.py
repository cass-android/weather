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


@app.route('/', methods=['GET'])

def index():
	timeframes = ['Hours', 'Days']	
	try:
		option = request.args.get("timeframes", type=str)

		if option == 'Future':
			return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_plot1(),
    				)
		
		elif option == 'Past':
			return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_plot3(),
    				)

		else:
		 return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_plot3(),
    				)

	except Exception as e:
		return str(e)
   
def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def create_layout():
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

    layout = go.Layout(
    title=go.layout.Title(
        text='Weather Forecast Tracker',
            font=dict(
                family='Helvetica, monospace',
                size=20
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
	    ),
	)

    return layout

def create_actuals(linewidth, days):
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
    # actuals
    x0 = [x.id for x in Current.query.filter(
    	Current.id >= now - datetime.timedelta(days=days)
    	).order_by(Current.id)]

    y0 = [x.drybulb for x in Current.query.filter(
    	Current.id >= now - datetime.timedelta(days=days)
    	).order_by(Current.id)]



    actuals = go.Scatter(
        x=x0,
        y=y0,
        name='actual temperature',
        mode='lines',
        line=dict(
            color = ('#696969'),
            width = linewidth)
        )  

    return actuals	

def create_plot1():
    # Variables
    linewidth=4
    h=48
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

    data=[create_actuals(linewidth, days=2)]

    # hourly for past n hours 
    for n in range(1,h):
        x = [x.id for x in Forecast.query.filter(
            Forecast.retrieval_time == now - datetime.timedelta(minutes=60*n)
        ).order_by(Forecast.id)]

        y = [x.drybulb for x in Forecast.query.filter(
            Forecast.retrieval_time == now - datetime.timedelta(minutes=60*n)
        ).order_by(Forecast.id)]

        # Colour gradient
        c1='#FF0000' #more distant
        c2= '#000099'
        mix=1-n/h

        if n in (1, h-1):
        	l= True
        else: 
        	l= False

        forecastHour = go.Scatter(
                x=x,
                y=y,
                name='{} h ago forecast'.format(n),
                line=dict(
                    color = (colorFader(c1,c2,mix)),
                    width = linewidth*(1/n)**(5/8),
                    ),
                showlegend=l
                )

        data.append(forecastHour)

    
    fig = go.Figure(data=data, layout=create_layout())
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_plot2():
    # Variables
    linewidth=4
    d=4
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

    data=[create_actuals(linewidt, days=2)]

    for n in range(0,d):
        x2 = [x.id for x in Forecast.query.filter(
            Forecast.retrieval_time == now - datetime.timedelta(days=n)
        ).order_by(Forecast.id)]

        y2 = [x.drybulb for x in Forecast.query.filter(
            Forecast.retrieval_time == now - datetime.timedelta(days=n)
        ).order_by(Forecast.id)]

        # Colour gradient
        c1='#FF0000' #more distant
        c2= '#000099' #nearer
        mix=1-(n+1)/d


        forecastDay = go.Scatter(
                x=x2,
                y=y2,
                name='{} d ago'.format(n),
                line=dict(
                    color = (colorFader(c1,c2,mix)),
                    width = linewidth*(1/(n+1))**(5/8),
                    ),
                showlegend=True,
                )

        data.append(forecastDay)

    fig = go.Figure(data=data, layout=create_layout())
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_plot3():

    
    d=4
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)	
    def generate_relative_sets(maxHoursOut=25):
        linewidth=4
        data=[create_actuals(linewidth, days=7)]

        for hoursOut in range (1,maxHoursOut):  

            # Colour gradient
            c1='#FF0000' #more distant
            c2= '#000099'
            mix=1-hoursOut /maxHoursOut

            # Legend visibility
            if hoursOut in (1, 6, 12, 18, maxHoursOut-1):
        	    l= True
            else: 
        	    l= False

            rel_set = go.Scatter(
                x=relative_set(hoursOut)[0],
                y=relative_set(hoursOut)[1],
                name='forecast {} h out'.format(hoursOut),
                line=dict(
                    color = (colorFader(c1,c2,mix)),
                    width = linewidth*(1/hoursOut)**(5/8),
                    ),
                showlegend=l
                )
            data.append(rel_set)
        
        return data

    def relative_set(hoursOut, hoursBack = 144):
        
        x = [x.id for x in Forecast.query.filter(
            Forecast.id >= now - datetime.timedelta(hours=hoursBack),
            Forecast.retrieval_time == Forecast.id - datetime.timedelta(hours=hoursOut)            
        ).order_by(Forecast.id)]

        y = [x.drybulb for x in Forecast.query.filter(
            Forecast.id >= now - datetime.timedelta(hours=hoursBack),
            Forecast.retrieval_time == Forecast.id - datetime.timedelta(hours=hoursOut)
        ).order_by(Forecast.id)]

        return x,y

    data = generate_relative_sets()
    fig = go.Figure(data=data, layout=create_layout())
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON2
