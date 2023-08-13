from flask import Blueprint, request
from datamanager.sql_data_manager import SQLDataManager
from Models import User, Movie, Review
from __inti__ import db

data_manager = SQLDataManager(db=db, users_model=User, movies_model=Movie, reviews_model=Review)
api = Blueprint('api', __name__)


# API: returns list of users in database
@api.route('/users', methods=['GET'])
def get_users():
    return data_manager.get_all_users()


# API: returns list of movies in a valid users list
@api.route('/users/<int:user_id>', methods=['GET'])
def get_user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    if movies is None:
        movies = "No user with that id"
    return movies


# API: Searches and adds a movie if valid to a valid users account
@api.route('/users/<int:user_id>/add_movie', methods=['POST'])
def add_movie_to_user(user_id):
    title = request.args.get('title')
    if not title:
        title = request.form.get('title')
    return data_manager.add_movie(user_id=user_id, title=title)
