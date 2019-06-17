"""
models imports app, so app can't import models
"""

from sqlalchemy.dialects.postgresql import JSON
from app import db

class Station(db.Model):
	__tablename__ = 'stations'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String())
	location = db.Column(db.Integer)
	
	def __init__(self, name, location):
		self.name = name
		self.location = location
		
	def __repr__(self):
		return '<id {}>'.format(self.id)	
		
class Historical(db.Model):
	__tablename__ = 'historicals'
	year = db.Column(db.Integer)
	month = db.Column(db.Integer)
	day = db.Column(db.Integer)
	time = db.Column(db.Integer)
	datetime = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	dewpoint = db.Column(db.Integer)
	relative_humidity = db.Column(db.Integer)
	wind_dir_10s_deg = db.Column(db.Integer)
	wind_spd_kmh = db.Column(db.Integer)
	visibility_km = db.Column(db.Integer)
	stn_press_kpa = db.Column(db.Integer)
	hmdx = db.Column(db.Integer)
	wind_chill = db.Column(db.Integer)
	weather = db.Column(db.Integer)
	
	def __init__(self, drybulb, dewpoint):
		self.drybulb = drybulb
		self.dewpoint = dewpoint
		self.timestamp = datetime

	def __repr__(self):
		return '<timestamp {}>'.format(self.datetime)

class Forecast(db.Model):
	__tablename__ = 'forecasts'
	datetime = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	dewpoint = db.Column(db.Integer)
	relative_humidity = db.Column(db.Integer)

	
	def __init__(self, drybulb, wetbulb):
		self.drybulb = drybulb
		self.dewpoint = dewpoint

	def __repr__(self):
		return '<id {}>'.format(self.id)		