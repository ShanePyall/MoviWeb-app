from api import api
from flask import render_template, request
from datamanager.sql_data_manager import SQLDataManager
from Models import User, Movie, Review
from __inti__ import db, app

app.register_blueprint(api, url_prefix='/api')
data_manager = SQLDataManager(db=db, users_model=User, movies_model=Movie, reviews_model=Review)


# On load: Displays home page, with option to view all users in database
@app.route("/")
def home():
    return render_template("home.html")


# Returns a list of all users.
@app.route('/users', methods=['GET'])
def list_users():
    users = data_manager.get_all_users()
    return render_template("users.html", users=users)


# Returns a list of a selected users movies
@app.route("/users/<int:user_id>", methods=['GET'])
def user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    if movies is None:
        movies = [{"title": "placeholder",
                   "rating": "0/0",
                   "director": "placeholder",
                   "year": "0",
                   "reviews": ["""I will go away after you add a movie"""]}]
    user_list = data_manager.get_all_users()
    user = [user for user in user_list if user['id'] == user_id]
    try:
        user = user[0]
        return render_template("users_movies.html", movies=movies, user=user)
    except IndexError:
        return route_not_found()


# Receives username, if not already in use, creates new user.
@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template("add_user.html")
    username = request.form.get("username")
    if len(username) > 15:
        return render_template("error.html", message=("Please only enter a username with 15 characters or less", 500))
    user_list = data_manager.get_all_users()
    username_list = [user['name'] for user in user_list]
    if username in username_list:
        return render_template("error.html", message=(f"Sorry, username: \"{username}\" already taken", 409))
    data_manager.add_new_user(username)
    return render_template("home.html")


# Deletes a user from the database
@app.route("/delete_user/<int:user_id>", methods=['GET', "POST"])
def delete_user(user_id):
    if request.method == "GET":
        user_list = data_manager.get_all_users()
        user = [user for user in user_list if user['id'] == user_id]
        try:
            user = user[0]
            return render_template("delete_user.html", user=user)
        except IndexError:
            return route_not_found()
    data_manager.delete_user(user_id)
    return render_template("home.html")


# Adds a new movie from omdbapi if name is valid and movie isn't already present in users movie list
@app.route("/users/<int:user_id>/add_movie", methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == "GET":
        return render_template("add_movie.html", user_id=user_id)
    title = request.form.get("title")
    if title == "":
        return render_template("error.html", message=("No data was entered for new movie", 500))
    movie_list = data_manager.get_user_movies(user_id)
    if movie_list is None:
        movie_list = [{'title': None}]
    for movie in movie_list:
        if movie['title'] == title:
            return render_template("error.html", message=(f"Sorry, movie: \"{title}\" is already in your list", 409))
    message = data_manager.add_movie(user_id=user_id, title=title)

    if type(message) == tuple:
        return render_template("error.html", message=message)
    return user_movies(user_id)


# Updates a selected movie in users list, changes retrieved data from omdbapi to users input.
@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == "GET":
        movie_list = data_manager.get_user_movies(user_id)
        target = [movie for movie in movie_list if movie['id'] == movie_id]
        try:
            movie = target[0]
            user = {"id": user_id}
            return render_template("update_movie.html", movie=movie, user=user)
        except IndexError:
            return route_not_found()

    title = request.form.get("title")
    director = request.form.get("director")
    year = request.form.get("year")
    rating = request.form.get("rating")
    data_manager.update_movie(user_id=user_id, movie_id=movie_id,
                              title=title, director=director, year=year, rating=rating)
    return render_template("home.html")


# Deletes a movie from users movie list
@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    if request.method == 'GET':
        movie_list = data_manager.get_user_movies(user_id)
        target = [movie for movie in movie_list if movie['id'] == movie_id]
        try:
            users = data_manager.get_all_users()
            user = [user for user in users if user['id'] == user_id]
            return render_template("delete_movie.html", user=user[0], movie=target[0])
        except IndexError:
            return route_not_found()
    data_manager.delete_movie(user_id, movie_id)
    return render_template("home.html")


# Adds a review to a movie in users list
@app.route("/users/<int:user_id>/review_movie/<int:movie_id>", methods=['GET', 'POST'])
def review_movie(user_id, movie_id):
    if request.method == "GET":
        movies = data_manager.get_user_movies(user_id)
        movie = [movie for movie in movies if movie['id'] == movie_id]
        users = data_manager.get_all_users()
        user = [user for user in users if user['id'] == user_id]
        return render_template("review_movie.html", movie=movie[0], user=user[0])

    review = request.form.get('review')
    if review is None or review == "":
        return home()
    if len(review) > 250:
        return render_template("error.html",
                               message=("""Too many characters,
                                        please use 250 characters or less for your review""", 500))
    data_manager.review_movie(user_id=user_id,
                              movie_id=movie_id,
                              review=review)
    return home()


# if route cannot be found, displays error html.
@app.errorhandler(404)
def not_found_error(e):
    message = ("""The content you are looking for, may not exist.\
If you entered the link manually, please double check your spelling""", e)
    return render_template("error.html", message=message), 404


# if method is not allowed, displays error html.
@app.errorhandler(TypeError)
def route_not_found(e):
    message = ("""Un-fortunately that route is in-accessible,\
Either the route does not exist or it is blocked for internal reasons.""", e)
    return render_template("error.html", message=message)


# If id is invalid, displays error.html
@app.errorhandler(IndexError)
def id_not_found(e):
    message = ("Un-fortunately that route could not be found, its likely the users and/or movies id is invalid.", e)
    return render_template("error.html", message=message)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
