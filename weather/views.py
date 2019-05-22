from __init__.py import app

# Set homepage
@app.route("/")
def home():
    return "Hello, World!"
    
# Set cassandra page    
@app.route("/cassandra")
def cass():
    return "Yo, Cass"
    
    
