"""
models imports app, so app can't import models
"""
from app import db

class Current(db.Model):
	__tablename__ = 'currents'
	id = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	relative_humidity = db.Column(db.Integer)

	
	def __init__(self, id, drybulb, relative_humidity):
		self.id = id
		self.drybulb = drybulb
		self.relative_humidity = relative_humidity

	def __repr__(self):
		return '<id {}>'.format(self.id)

class Forecast(db.Model):
	__tablename__ = 'forecasts'
	id = db.Column(db.DateTime, primary_key=True)
	retrieval_time = db.Column(db.DateTime, primary_key=True)
	drybulb = db.Column(db.Integer)
	relative_humidity = db.Column(db.Integer)


	def __init__(self, id, retrieval_time, drybulb, relative_humidity):
		self.retrieval_time = retrieval_time
		self.id = id
		self.drybulb = drybulb
		self.relative_humidity = relative_humidity

	def __repr__(self):
		return '<id {}>'.format(self.id)		