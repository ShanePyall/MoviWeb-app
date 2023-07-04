import json
import requests
from .data_manager_interface import DataManagerInterface

API_KEY = 'be04b8e5'
DATA_LINK = f"http://www.omdbapi.com/?apikey={API_KEY}&t="


# Derives from parent class DataManagerInterface
class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    # Return a list of all users
    def get_all_users(self):
        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())
        return user_list

    # Return a list of all movies for a given user
    def get_user_movies(self, user_id):
        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())
        user = [user for user in user_list if user['id'] == user_id]
        user = user[0]
        return user['storage']

    # Adds a new user to user_list
    def add_new_user(self, username):
        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())
        id_list = [item['id'] for item in user_list]
        id_list.sort()
        try:
            unique_id = int(id_list[-1]) + 1
        except IndexError:
            unique_id = 0
        storage = [{"id": 0, "title": "placeholder", "director": "placeholder", "year": "0", "rating": "0"}]
        user_dict = {"id": unique_id, "name": username, "storage": storage}
        user_list.append(user_dict)
        with open(self.filename, "w") as writable:
            writable.write(json.dumps(user_list, indent=2))
        return

    def delete_user(self, user_id):
        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())
        for user in user_list:
            if user['id'] == user_id:
                user_list.remove(user)
        with open(self.filename, "w") as writable:
            writable.write(json.dumps(user_list, indent=2))
        return

    # Adds a movie to user's storage list
    def add_movie(self, user_id, title):
        title = title.replace(" ", "+")
        res = requests.get(DATA_LINK + title)
        parsed = res.json()
        if parsed["Response"] == "False":
            message = f"\nSorry, we couldn't find {title} anywhere. Please double check your spelling"
            return message, 404

        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())

        user = [user for user in user_list if user['id'] == user_id]
        user = user[0]
        id_list = [movie['id'] for movie in user['storage']]
        id_list.sort()
        try:
            unique_id = int(id_list[-1]) + 1
        except IndexError:
            unique_id = 0

        new_movie = {"id": unique_id, "title": parsed["Title"], "director": parsed["Director"],
                     "year": parsed["Year"], "rating": parsed["Ratings"][0]["Value"]}

        for user in user_list:
            if user['id'] == user_id:
                user['storage'].append(new_movie)

        with open(self.filename, "w") as writable:
            writable.write(json.dumps(user_list, indent=2))
        return

    # Deletes a movie from a user's storage list
    def delete_movie(self, user_id, movie_id):
        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())
        user = [user for user in user_list if user['id'] == user_id]
        user = user[0]

        target = [movie for movie in user['storage'] if movie['id'] == movie_id]
        target = target[0]
        for user in user_list:
            if user['id'] == user_id:
                user['storage'].remove(target)

        with open(self.filename, "w") as writeable:
            writeable.write(json.dumps(user_list, indent=2))
        return

    # Updates a movie in user's storage list
    def update_movie(self, user_id, movie_id, title, director, year, rating):
        with open(self.filename, "r") as readable:
            user_list = json.loads(readable.read())

        for user in user_list:
            if user['id'] == user_id:
                for movie in user['storage']:
                    if movie['id'] == movie_id:
                        if title != '':
                            movie['title'] = title
                        if director != '':
                            movie['director'] = director
                        if year != '':
                            movie['year'] = year
                        if rating != '':
                            movie['rating'] = rating

        with open(self.filename, "w") as writable:
            writable.write(json.dumps(user_list, indent=2))
        return
