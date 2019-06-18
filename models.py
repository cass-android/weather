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
	id = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	dewpoint = db.Column(db.Integer)
	relative_humidity = db.Column(db.Integer)
	
	def __init__(self, drybulb, dewpoint):
		self.drybulb = drybulb
		self.dewpoint = dewpoint

	
	def __repr__(self):
		return '<id {}>'.format(self.id)


class Forecast(db.Model):
	__tablename__ = 'forecasts'
	id = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	dewpoint = db.Column(db.Integer)
	relative_humidity = db.Column(db.Integer)

	
	def __init__(self, drybulb, wetbulb):
		self.drybulb = drybulb
		self.dewpoint = dewpoint

	def __repr__(self):
		return '<id {}>'.format(self.id)		