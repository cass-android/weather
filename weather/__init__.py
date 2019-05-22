from flask import Flask, render_template, request
from weather.database import db_session

import weather.views

app = Flask(__name__)
@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()

if __name__ == "__main__":
    app.run(debug=True)











