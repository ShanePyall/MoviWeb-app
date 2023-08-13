from datamanager.data_manager_interface import DataManagerInterface
import requests


API_KEY = 'be04b8e5'
DATA_LINK = f"http://www.omdbapi.com/?apikey={API_KEY}&t="


# Translates sql data received to data app.py can use
def movie_sql_to_app_formatter(data, reviews=None):
    movie_dict = {'id': data.id, 'title': data.title,
                  'director': data.director, 'year': data.year,
                  'rating': data.rating,
                  'reviews': reviews}
    return movie_dict


# Derives from parent class DataManagerInterface
class SQLDataManager(DataManagerInterface):
    def __init__(self, db, users_model, movies_model, reviews_model):
        self.db = db
        self.Users = users_model
        self.Movie = movies_model
        self.Review = reviews_model

    # Return a list of all users
    def get_all_users(self):
        all_users = self.Users.query.all()
        user_list = []
        for user in all_users:
            user_list.append({"id": user.user_id, "name": user.name})
        return user_list

    # Return a list of all movies for a given user
    def get_user_movies(self, user_id):
        user = self.Users.query.filter_by(user_id=user_id).first()
        if not user:
            return
        movies = user.movie_ids
        if movies == '' or movies is None:
            return "No movies tied to this account"
        if ", " in movies:
            movies_id_list = movies.split(", ")
        else:
            movies_id_list = [movies]
        movie_list = []

        # Raw movie list
        for movie_id in movies_id_list:
            if movie_id != "":
                movie_table = self.Movie.query.all()
                for movie in movie_table:
                    if movie.id == int(movie_id):
                        movie_list.append(movie)

        reviews = self.Review.query.filter_by(user_id=user_id).all()
        formated_list = []
        no_reviews = ["No reviews yet"]
        for movie in movie_list:
            if not reviews:
                movie_reviews = no_reviews
            else:
                movie_reviews = [review.review_details for review in reviews if review.movie_id == movie.id]
                if not movie_reviews:
                    movie_reviews = no_reviews
            formated_list.append(movie_sql_to_app_formatter(data=movie,
                                                            reviews=movie_reviews))
        return formated_list

    # Adds a new user to user_list
    def add_new_user(self, name):
        self.db.session.add(self.Users(name=name))
        self.db.session.commit()

    # Deletes a user with the appropriate id
    def delete_user(self, user_id):
        self.db.session.query(self.Users).filter(self.Users.user_id == user_id).delete()
        self.db.session.commit()

    # Adds a movie to user's storage list
    def add_movie(self, user_id, title):
        if not title:
            title = " "
        fixed_title = title.replace(" ", "+")
        res = requests.get(DATA_LINK + fixed_title)
        parsed = res.json()
        if parsed["Response"] == "False":
            message = f"\nSorry, we couldn't find \"{title}\" anywhere. Please double check your spelling"
            return message, 404

        movie_titles_list = self.Movie.query.with_entities(self.Movie.title)
        title_checker_list = []
        for movie in movie_titles_list:
            title_checker_list.append(movie[0])
        if parsed['Title'] not in title_checker_list:  # If movie isn't in database, add to database.
            self.db.session.add(self.Movie(title=parsed['Title'],
                                           director=parsed['Director'],
                                           year=parsed['Year'],
                                           rating=parsed['Ratings'][0]['Value']))

        user = self.Users.query.filter_by(user_id=user_id).first()
        if user is None:
            message = "\nSorry, we couldn't find this user in our database"
            return message, 404
        if user.movie_ids == "" or user.movie_ids is None:  # If users movie list is empty
            user_movies_id_list = []
        else:
            if ", " in user.movie_ids:
                user_movies_id_list = user.movie_ids.split(", ")  # Split so only int values remain
            else:
                user_movies_id_list = list(user.movie_ids)  # If there's only one movie in users list

        users_movie_storage = []
        for movie_id in user_movies_id_list:
            if movie_id != "":
                users_movie_storage.append(int(movie_id))
        target_movie = self.Movie.query.filter_by(title=parsed['Title']).first()
        if target_movie.id in users_movie_storage:
            message = f"\n\"{target_movie.title}\" is already in {user.name}s' list"
            return message, 500

        if user.movie_ids is None:
            user.movie_ids = str(target_movie.id)
        else:
            user.movie_ids += ", " + str(target_movie.id)
        self.db.session.commit()
        return "Movie added to user list", 200

    # Deletes a movie from a user's storage list
    def delete_movie(self, user_id, movie_id):
        user = self.Users.query.filter_by(user_id=user_id).first()
        movie_id_list = user.movie_ids.split(", ")
        updated_list = ""
        if str(movie_id) in movie_id_list:
            movie_id_list.remove(str(movie_id))
        else:
            return "Not in the list"
        user.movie_ids = updated_list
        self.db.session.commit()
        return "Deleted"

    # Updates a movie in user's storage list
    def update_movie(self, user_id, movie_id, title="", director="", year="0", rating=""):
        print(f"user :{user_id}. updating movie with id: {movie_id}...")
        target_movie = self.Movie.query.filter_by(id=movie_id).first()
        if title != '':
            target_movie.title = str(title)
        if director != '':
            target_movie.director = str(director)
        if year != '':
            try:
                target_movie.year = int(year)
            except ValueError:
                print(f"'{year}' wasn't a valid input")
        if rating != '':
            target_movie.rating = str(rating)
        self.db.session.commit()
        return "updated"

    # Allows user to write a review of a movie of their choice
    def review_movie(self, user_id, movie_id, review):
        movie = self.Movie.query.filter_by(id=movie_id).first()
        user = self.Users.query.filter_by(user_id=user_id)
        if movie is None or user is None or review is None:
            return
        self.db.session.add(self.Review(user_id=user_id,
                                        movie_id=movie_id,
                                        review_details=review))
        self.db.session.commit()
        return


"""
Schema:
Notes=
no table per user(bad practise)

tables:(ignoring main id)
movies = movies
users = users, movie_ids
reviews = user_id, movie_id, review_details

"""