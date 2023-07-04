from abc import ABC, abstractmethod

API_KEY = 'be04b8e5'
DATA_LINK = f"http://www.omdbapi.com/?apikey={API_KEY}&t="


# Translates user data stored in a storage file (E.g. json, csv etc)
class DataManagerInterface(ABC):

    # Returns a list of all users
    @abstractmethod
    def get_all_users(self):
        pass

    # Returns a list of movies from user with users id
    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    # Adds a new user to user_list
    @abstractmethod
    def add_new_user(self, username):
        pass

    # Deletes a user from user list with users id
    @abstractmethod
    def delete_user(self, user_id):
        pass

    # Adds movie to users movie list
    @abstractmethod
    def add_movie(self, user_id, title):
        pass

    # Deletes movie from users movie list
    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        pass

    # Updates movie in users movie list
    @abstractmethod
    def update_movie(self, user_id, movie_id, title, director, year, rating):
        pass
