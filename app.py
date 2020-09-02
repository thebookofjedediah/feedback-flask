from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db

app = Flask(__name__)
# ADD YOUR DB HERE 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = "hihihi333"
# Redirects are not blocked here - set this next line to True or delet it in order to enable them
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

# HOME PAGE ROUTE W/LIST
@app.route('/')
def get_home():
    """Home Page"""
    return render_template('home.html')