"""
views imports app and models; these don't import views
"""
# -*- coding: utf-8 -*-

from flask import render_template, request
from sqlalchemy.sql.expression import func
from app import app, db
from models import Forecast, Current
import datetime
import plotly
from plotly import graph_objs as go
from plotly import plotly as py 
from plotly import tools
import matplotlib as mpl
import pandas as pd
import numpy as np 
import json


@app.route('/project', methods=['GET'])
def project():
    return render_template('project.html')


@app.route('/', methods=['GET'])
def index():
	timeframes = []	
	try:
		option = request.args.get("timeframes", type=str) # gets the value of 'timeframes' (the submitted form that makes the request)

		if option == 'Future':
			return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_plot(skip=3, linewidth=4, hoursBack=12, hoursForward=120, maxHoursOut=121)
    				)	
		elif option == 'Past':
			return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_plot(skip=3, linewidth=4, hoursBack=144, hoursForward=0, maxHoursOut=121),
    				)
		elif option == 'All':
		    return render_template(
				    'index.html', 
				    timeframes=timeframes, 
				    plot=create_plot(skip=4, linewidth=4, hoursBack=84, hoursForward=96, maxHoursOut=121),
				    )
		else:
		 return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_plot(skip=4, linewidth=4, hoursBack=84, hoursForward=96, maxHoursOut=121),
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
    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='Temperature \u2103',
            font=dict(
                family='Helvetica, monospace',
                size=18
	            )
	        )
	    ),
    margin=go.layout.Margin(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
        ),
    hovermode = 'closest'
	)

    return layout

def create_now():
	now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
	x = [now, now]
	y = [0, 30]

	nowtrace = go.Scatter(
		x=x,
		y=y,
		name='current time',
		mode='lines',
		showlegend=False,
		line=dict(
			color =('#EFB805'),
			width = 4)
		)

	return nowtrace


def create_actuals(linewidth, hoursBack, showlegend=False):
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
    # actuals
    x0 = [x.id for x in Current.query.filter(
    	Current.id >= now - datetime.timedelta(hours=hoursBack)
    	).order_by(Current.id)]

    y0 = [x.drybulb for x in Current.query.filter(
    	Current.id >= now - datetime.timedelta(hours=hoursBack)
    	).order_by(Current.id)]


    actuals = go.Scatter(
        x=x0,
        y=y0,
        name='actual temperature',
        mode='lines',
        showlegend=showlegend,
        line=dict(
            color = ('#c0c0c0'),
            width = 4)
        )  

    return actuals

def create_latest_forecast(hoursBack, hoursForward, linewidth=3):
# Creates trace for most recent forecast only; currently not used

    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
    query = Forecast.query.filter(
        Forecast.id >= now - datetime.timedelta(hours=hoursBack),
        Forecast.id <= now + datetime.timedelta(hours=hoursForward),
        Forecast.retrieval_time == db.session.query(func.max(Forecast.retrieval_time))[0]            
    ).order_by(Forecast.id)


    latest = go.Scatter(
        x = [x.id for x in query],
        y = [x.drybulb for x in query],
        name='latest forecast',
        mode='lines',
        line=dict(
            color = '#000000',
            width = linewidth,
            ),
        hoverinfo='x+y',
        showlegend=True
        )

    return latest


def create_plot(skip=1, linewidth=4, hoursBack=168, hoursForward=120, maxHoursOut=192):
    data=[create_actuals(linewidth=linewidth, hoursBack=hoursBack), create_now()]
    hourWindow=range(1,maxHoursOut)[::skip]
    

    for hour in hourWindow:

        # Colour gradient
        c1= '#000099' #more distant
        c2= '#FF0000'

        # crimson '#DC143C'
        mix=1-hour/maxHoursOut

        rel_set = go.Scatter(
            x=relative_set(hoursBack=hoursBack, hoursOut=hour, hoursForward=hoursForward)[0],
            y=relative_set(hoursBack=hoursBack, hoursOut=hour, hoursForward=hoursForward)[1],
            name='forecast {} h out'.format(hour),
            mode='lines',
            line=dict(
                color = (colorFader(c1,c2,mix)),
                width = (linewidth*1.5)*(1/hour)**(6/8),
                ),
            hoverinfo='x+y',
            showlegend=True
            )
        data.append(rel_set)
    
    fig = go.Figure(data=data, layout=create_layout())
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def relative_set(hoursOut, hoursBack, hoursForward):
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)       
    query = Forecast.query.filter(
        Forecast.id >= now - datetime.timedelta(hours=hoursBack),
        Forecast.id <= now + datetime.timedelta(hours=hoursForward),
        Forecast.retrieval_time == Forecast.id - datetime.timedelta(hours=hoursOut)            
    ).order_by(Forecast.id)

    x = [x.id for x in query]
    y = [x.drybulb for x in query]

    return x,y
