from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserRegistrationForm, UserLoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
# ADD YOUR DB HERE 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', "mysecret1")
# Redirects are not blocked here - set this next line to True or delet it in order to enable them
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

# HOME PAGE ROUTE W/LIST
@app.route('/')
def get_home():
    """Home Page"""
    feedbacks = Feedback.query.all()
    return render_template('home.html', feedbacks=feedbacks)

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
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username is taken")
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash(f"Welcome {first_name}, we successfully created your account!", "success")
        return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form=form)

# LOG IN AS USER
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}", "success")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)

# logout
@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Unsafely logged out", "warning")
    return redirect('/')

# USER DETAILS PAGE
@app.route('/users/<username>')
def get_user_information(username):
    if "username" not in session or username != session['username']:
        flash("You are not authorized to view that page", "danger")
        return redirect('/')
    user = User.query.get(username)
    return render_template('user_details.html', user=user)

# ADD FEEDBACK FORM
@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    form = FeedbackForm()

    if "username" not in session or username != session['username']:
        flash("You are not authorized to view that page", "danger")
        return redirect('/')
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash("New Feedback Added", "success")
        return redirect(f"/users/{username}")

    user = User.query.get(username)
    return render_template('add_feedback.html', user=user, form=form)

# FEEDBACK DETAILS
@app.route('/feedback/<int:id>')
def get_feedback_details(id):
    feedback = Feedback.query.get_or_404(id)

    return render_template('feedback_details.html', feedback=feedback)

# EDIT FEEDBACK
@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def feedback_edit(id):
    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj=feedback)
    if "username" not in session:
        flash("please login first", "warning")
        return redirect('/login')
    
    if feedback.username != session["username"]:
        flash("That is not your post", "danger")
        return redirect('/')

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    
    return render_template('edit_feedback.html', form=form, feedback=feedback, username=session["username"])

# DELETE FEEDBACK
@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    """Delete the feedback"""
    if "username" not in session:
        flash("please login first", "warning")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(id)
    if feedback.username == session["username"]:
        db.session.delete(feedback)
        db.session.commit()
        flash("DELETED", "success")
        return redirect(f"/users/{feedback.username}")
    flash("You don't have permission to delete that", "danger")
    return redirect('/')