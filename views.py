"""
views imports app and models; these don't import views
"""

from flask import render_template, request
from app import app
from models import Historical, Forecast, Station
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
 	today = datetime.date.today()
 	x1 = [x.id for x in Historical.query.filter(Historical.id >= today - datetime.timedelta(days=7)).order_by(Historical.id)]
 	y1 = [x.drybulb for x in Historical.query.filter(Historical.id >= today - datetime.timedelta(days=7)).order_by(Historical.id)]

 	x2 = [x.id for x in Forecast.query.all()]
 	y2 = [x.drybulb for x in Forecast.query.all()]

 	historicals = go.Line(
 			x=x1,
 			y=y1,
 			name='historicals'
 			)

 	forecasts = go.Line(
 			x=x2,
 			y=y2,
 			name='forecasts'
 			)

 	data = [historicals, forecasts]
 	graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

 	return graphJSON

 	"""
 	df = pd.DataFrame(Historical.query.all())
    chart_data = json.loads(df.to_json(orient='records'))    
    data = {'chart_data': chart_data}
"""