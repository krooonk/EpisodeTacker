from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db=SQLAlchemy()

class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True, nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    password_hash=db.Column(db.String,nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))


series_genre=db.Table("series_genre",
                      db.Column("genre_id",db.Integer,db.ForeignKey("genre.id"),primary_key=True),
                      db.Column("series_id",db.Integer,db.ForeignKey("series.id"),primary_key=True))


class Series(db.Model):
    __tablename__="series"
    id=db.Column(db.Integer,primary_key=True)
    tmdb_id=db.Column(db.Integer,unique=True,nullable=False)
    title=db.Column(db.String,nullable=False)
    description=db.Column(db.Text)
    origin_country=db.Column(db.String)
    first_air_date=db.Column(db.String)
    actors=db.Column(db.String)
    creators=db.Column(db.String)
    tmdb_vote_average=db.Column(db.Float)
    num_seasons=db.Column(db.SmallInteger)
    num_eps=db.Column(db.Integer)
    poster_filename=db.Column(db.String)
    status=db.Column(db.String,default="Ended")
    source=db.Column(db.String,default="initial_scrape")
    last_synced_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    genres=db.relationship("Genre",secondary=series_genre,backref="series")


class Genre(db.Model):
    __tablename__="genre"
    id=db.Column(db.Integer, primary_key=True)
    tmdb_id=db.Column(db.Integer,unique=True,nullable=False)
    name=db.Column(db.String,unique=True,nullable=False)


class Season(db.Model):
    __tablename__="season"
    id=db.Column(db.Integer,primary_key=True)
    series_id=db.Column(db.Integer,db.ForeignKey("series.id"),nullable=False)
    season_number=db.Column(db.SmallInteger,nullable=False)
    num_eps=db.Column(db.Integer)


class Episode(db.Model):
    __tablename__="episode"
    id=db.Column(db.Integer, primary_key=True)
    season_id=db.Column(db.Integer,db.ForeignKey("season.id"),nullable=False)
    episode_number=db.Column(db.Integer,nullable=False)
    title=db.Column(db.String)
    description=db.Column(db.Text)

class UserWatchEpisode(db.Model):
    __tablename__="user_watch_episode"
    ep_id=db.Column(db.Integer,db.ForeignKey("episode.id"),primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"), primary_key=True)
    watched_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))


class UserSeriesRating(db.Model):
    __tablename__="user_series_rating"
    series_id=db.Column(db.Integer,db.ForeignKey("series.id"),primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),primary_key=True)
    rating=db.Column(db.Float)
    notes=db.Column(db.Text)
    created_at=db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))