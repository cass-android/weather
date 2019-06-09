""" 
this module is where the flask instance and database live. 
It's imported in a lot of other places, so keep it thin to
avoid circular imports
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
