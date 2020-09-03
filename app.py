from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import UserRegistrationForm, UserLoginForm

app = Flask(__name__)
# ADD YOUR DB HERE 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
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

# USER REGISTRATION
# To Do ***************************
# Error handling for taken username
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash(f"Welcome {first_name}, we successfully created your account!")
        return redirect('/secret')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}")
            session['username'] = user.username
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)

# logout
@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Unsafely logged out")
    return redirect('/')

# SECRET PAGE
@app.route('/secret')
def get_secret():
    if "username" not in session:
        flash("Please login first!")
        return redirect('/')
    
    return render_template('secret.html')