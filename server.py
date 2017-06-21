"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    a = jsonify([1, 3])
    return render_template('homepage.html')


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():
    """Shows a registration form for user email address and password."""

    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Registers new user, checks for existing user"""
    # Check for existing user
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter(User.email == email).first():
        return redirect("/login")

    else:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

    return redirect("/")


@app.route("/login", methods=["GET"])
def login_form():
    """Allows the user to enter login info."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def log_user_in():
    """Logs in the user if details match."""
    email = request.form.get("email")
    password = request.form.get("password")
    # Check db for email and pw
    if User.query.filter(User.email == email,
                         User.password == password).first():
        session['user'] = db.session.query(User.user_id).first()
        flash('Logged in')

    else:
        flash('Incorrect email/password')

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
