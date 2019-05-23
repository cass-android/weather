from app import db
from sqlalchemy.dialects.postgresql import JSON

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
	datetime = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	wetbulb = db.Column(db.Integer)
	
	def __init__(self, drybulb, wetbulb):
		self.drybulb = drybulb
		self.wetbulb = wetbulb

	def __repr__(self):
		return '<id {}>'.format(self.id)	

class Forecast(db.Model):
	__tablename__ = 'forecasts'
	id = db.Column(db.Integer, primary_key=True)
	datetime = db.Column(db.DateTime)
	forecasttime = db.Column(db.DateTime)
	drybulb = db.Column(db.Integer)
	wetbulb = db.Column(db.Integer)
	
	def __init__(self, drybulb, wetbulb):
		self.drybulb = drybulb
		self.wetbulb = wetbulb

	def __repr__(self):
		return '<id {}>'.format(self.id)		