from __inti__ import db, app


# Creates a list of users
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # Foreign key
    movie_ids = db.Column(db.String, nullable=True)


# Creates a new movie object
class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    director = db.Column(db.String(50))
    year = db.Column(db.Integer)
    rating = db.Column(db.String(10))
    # note = db.Column(db.String(50))


# Creates a list of reviews, by users of movies
class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)  # Foreign key
    movie_id = db.Column(db.Integer)  # Foreign key
    review_details = db.Column(db.String(250))

