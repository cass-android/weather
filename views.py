"""
views imports app and models; these don't import views
"""

from flask import render_template
from app import app
from models import Historical, Forecast, Station

@app.route('/')
def index():
    df = Historical.query().all()
    chart_data = df.to_dict(orient='records')
    chart_data = json.dumps(chart_data, indent=2)
    data = {'chart_data': chart_data}
    return render_template("index.html", data=data)    
    
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
	return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run(debug=True)
