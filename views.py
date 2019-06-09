"""
views imports app and models; these don't import views
"""

from flask import render_template, request
from app import app
from models import Historical, Forecast, Station

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
 	x = [x.datetime for x in Historical.query.all()]
 	y = [x.drybulb for x in Historical.query.all()]

 	data = [
 		go.Line(
 			x=x,
 			y=y
 			)
 		]
 	graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

 	return graphJSON

 	"""
 	df = pd.DataFrame(Historical.query.all())
    chart_data = json.loads(df.to_json(orient='records'))    
    data = {'chart_data': chart_data}
"""