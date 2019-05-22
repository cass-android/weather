from sqlalchemy import Column, Integer, String
from weather.database import Base

class Station(Base):
	__tablename__= "stations"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True)
	latitude = db.Column(db.Integer)
	longitude = db.Column(db.Integer)
	

class Historical(Base):
	__tablename__="historicals"
	timestamp = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	wetbulb = db.Column(db.Integer)
	
class Forecast(Base):
	__tablename__="forecasts"
	timestamp = db.Column(db.DateTime, primary_key=True)
	retrieved_on = db.Column(db.DateTime)
	drybulb = db.Column(db.Integer)
	wetbulb = db.Column(db.Integer)
	