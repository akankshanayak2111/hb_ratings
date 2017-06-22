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


@app.route("/users/<user_id>", methods=["GET"])
def user_details(user_id):
    """Shows a user's details."""

    user = User.query.get(user_id)
    user_ratings = user.ratings
    user_movies = []
    for rating in user_ratings:
        user_movies.append((rating.movie.title, rating.score))

    return render_template("user_details.html",
                           user=user,
                           user_movies=user_movies)


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
        flash('Email already exists, please login.')

    else:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Successfully registered new user, please login.')

    return redirect("/login")


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

    user = User.query.filter(User.email == email).first()

    if user and user.password == password:
        session['user'] = user.user_id
        flash('Logged in')
        return redirect("/users/{}".format(user.user_id))

    else:
        flash('Incorrect email/password')
        return redirect("/login")


@app.route("/logout")
def log_user_out():
    """Logs out the user."""
    # session.clear()
    session.pop('user')
    flash('Logged out')

    return redirect("/")


@app.route("/movies")
def movie_list():
    """Shows the list of movies."""
    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movie/<movie_id>", methods=["GET"])
def movie_details(movie_id):
    """Shows a movie's details."""

    movie = Movie.query.get(movie_id)
    movie_ratings = movie.ratings

    return render_template("movie_details.html",
                           movie=movie,
                           movie_ratings=movie_ratings)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
