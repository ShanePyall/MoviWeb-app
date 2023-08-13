from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Defines location of sql database
filepath = os.path.abspath(os.getcwd()) + "\\user_list.sqlite"

# Defines app engine
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + filepath
db = SQLAlchemy()
db.init_app(app)
