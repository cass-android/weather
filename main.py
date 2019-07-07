"""
use this to run the app
"""
from app import app
from views import *
from models import *
import os

if __name__ == '__main__':
    app.run()
