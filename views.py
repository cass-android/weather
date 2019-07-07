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
	try:
		option = request.args.get("timeframes", type=str) # gets the value of 'timeframes' from the form that submits request

		if option == 'Future':
			return render_template(
    				'index.html', 
    				plot=create_plot(skip=3, linewidth=4, hoursBack=12, hoursForward=120, maxHoursOut=121)
    				)	
		elif option == 'Past':
			return render_template(
    				'index.html', 
    				plot=create_plot(skip=4, linewidth=4, hoursBack=144, hoursForward=0, maxHoursOut=96),
    				)
		elif option == 'All':
		    return render_template(
				    'index.html', 
				    plot=create_plot(skip=4, linewidth=4, hoursBack=84, hoursForward=96, maxHoursOut=121),
				    )
		else:
		 return render_template(
    				'index.html', 
    				plot=create_plot(skip=4, linewidth=4, hoursBack=84, hoursForward=96, maxHoursOut=121),
    				)

	except Exception as e:
		return str(e)
   
def colorFader(c1,c2,mix=0): 
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
		name='current hour',
		mode='lines',
		showlegend=False,
		hoverinfo='x+name',
		line=dict(
			color =('#EFB805'),
			width = 4)
		)

	return nowtrace


def create_actuals(linewidth, hoursBack, showlegend=False):
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

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


def create_plot(skip=1, linewidth=4, hoursBack=168, hoursForward=120, maxHoursOut=192):
    data=[create_actuals(linewidth=linewidth, hoursBack=hoursBack), create_now()]
    hourWindow=range(1,maxHoursOut)[::skip]
    
    for hour in hourWindow:
        # Defines parameters for colour gradient (uses linear interpolation)
        c1= '#000099' # more distant forecasts
        c2= '#FF0000' # nearer forecasts
        mix=1-hour/maxHoursOut
        
        # Creats Plotly graph object for each forecast set
        rel_set = go.Scatter(
        	text=relative_set(hoursBack=hoursBack, hoursOut=hour, hoursForward=hoursForward)[2],
            x=relative_set(hoursBack=hoursBack, hoursOut=hour, hoursForward=hoursForward)[0],
            y=relative_set(hoursBack=hoursBack, hoursOut=hour, hoursForward=hoursForward)[1],
            name='forecast {} h out'.format(hour),
            mode='lines',
            line=dict(
                color = (colorFader(c1,c2,mix)),
                width = (linewidth*1.5)*(1/hour)**(6/8),
                ),
            hovertemplate='Forecast on: %{text}<br>' +
                        'For: %{x}<br>'+
                        'Temp: %{y} \u2103 <br>' +
                        '<extra></extra>',
            showlegend=True
            )
        data.append(rel_set)
    
    # Combines graph objects into a figure that's sent to our template
    fig = go.Figure(data=data, layout=create_layout())
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def relative_set(hoursOut, hoursBack, hoursForward):
# returns a set of forecasts within a specified time window, with retrieval time relative to forecast id

    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)       
    query = Forecast.query.filter(
        Forecast.id >= now - datetime.timedelta(hours=hoursBack),
        Forecast.id <= now + datetime.timedelta(hours=hoursForward),
        Forecast.retrieval_time == Forecast.id - datetime.timedelta(hours=hoursOut)            
    ).order_by(Forecast.id)

    x = [x.id for x in query]
    y = [x.drybulb for x in query]
    t = [x.retrieval_time for x in query]

    return x,y,t
