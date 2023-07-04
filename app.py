from flask import Flask, render_template, request
from datamanager.json_data_manager import JSONDataManager

app = Flask(__name__)
data_manager = JSONDataManager('datamanager/user_list.json')


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
    movie_list = data_manager.get_user_movies(user_id)
    for movie in movie_list:
        if movie['title'] == title:
            return render_template("error.html", message=(f"Sorry, movie: \"{title}\" is already in your list", 409))
    message = data_manager.add_movie(user_id=user_id, title=title)

    if type(message) == tuple:
        return render_template("error.html", message=message[0])
    return user_movies(user_id)


# Updates a selected movie in users list, changes retrieved data from omdbapi to users input.
@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == "GET":
        movie_list = data_manager.get_user_movies(user_id)
        target = [movie for movie in movie_list if movie['id'] == movie_id]
        try:
            movie = target[0]
            return render_template("update_movie.html", movie=movie, user_id=user_id)
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
            movie = target[0]
            return render_template("delete_movie.html", user_id=user_id, movie=movie)
        except IndexError:
            return route_not_found()
    data_manager.delete_movie(user_id, movie_id)
    return render_template("home.html")


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
    app.run(debug=True)
