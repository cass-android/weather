"""
use this to run the app
"""
from app import app, db
from models import *
from views import *
import os

if __name__ == '__main__':
	app.run()
