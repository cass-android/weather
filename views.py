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


@app.route('/project', methods=['GET'])
def project():
    return render_template('project.html')


@app.route('/', methods=['GET'])

def index():
	timeframes = ['Hours', 'Days']	
	try:
		option = request.args.get("timeframes", type=str)

		if option == 'Future':
			return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_future(hoursBack=12,linewidth=4),
    				)
		
		elif option == 'Past':
			return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_past(),
    				)
		elif option == 'All':
		    return render_template(
				    'index.html', 
				    timeframes=timeframes, 
				    plot=create_future(hoursBack=96,linewidth=4),
				    )
		else:
		 return render_template(
    				'index.html', 
    				timeframes=timeframes, 
    				plot=create_past(),
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
	)

    return layout

def create_actuals(linewidth, hoursBack):
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
        line=dict(
            color = ('#696969'),
            width = linewidth)
        )  

    return actuals	

def create_future(hoursBack, linewidth=4):
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
    data=[create_actuals(linewidth=linewidth, hoursBack=hoursBack)]

    # hourly for past n hours 
    for n in range(1,hoursBack):
        query = Forecast.query.filter(
            Forecast.retrieval_time == now - datetime.timedelta(hours=n)
        ).order_by(Forecast.id)

        x = [x.id for x in query]
        y = [x.drybulb for x in query]

        # Colour gradient
        c1='#FF0000' #more distant
        c2= '#000099'
        mix=1-n/hoursBack

        if n in (1, 6, 12, 18, hoursBack-1):
        	l= True
        else: 
        	l= False

        forecastHour = go.Scatter(
                x=x,
                y=y,
                name='forecast {} h ago '.format(n),
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

def create_past(linewidth=4, hoursBack=168, hoursForward = 12):
    now = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)	

    def generate_relative_sets(maxHoursOut=25):       
        data=[create_actuals(linewidth=linewidth, hoursBack=hoursBack)]

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

    def relative_set(hoursOut, hoursBack = hoursBack, hoursForward = hoursForward):       
        query = Forecast.query.filter(
            Forecast.id >= now - datetime.timedelta(hours=hoursBack),
            Forecast.id <= now + datetime.timedelta(hours=hoursForward),
            Forecast.retrieval_time == Forecast.id - datetime.timedelta(hours=hoursOut)            
        ).order_by(Forecast.id)

        x = [x.id for x in query]
        y = [x.drybulb for x in query]

        return x,y

    data = generate_relative_sets()
    fig = go.Figure(data=data, layout=create_layout())
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON2
