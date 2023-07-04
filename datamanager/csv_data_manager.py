import csv

from .data_manager_interface import DataManagerInterface


class CSVDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def get_all_users(self):
        # Return a list of all users
        pass

    def add_new_user(self, username):
        pass

    def delete_user(self, user_id):
        pass

    def get_user_movies(self, user_id):
        # Return a list of all movies
        pass

    def add_movie(self, user_id, title):
        pass

    def update_movie(self, user_id, movie_id, title, director, year, rating):
        pass

    def delete_movie(self, user_id, movie_id):
        pass
