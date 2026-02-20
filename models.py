"""
models.py
-----------
Defines all tables necessary for the EpisodeTracker database.
The actual creation of the tables happens when the create_db.py script is run.
"""

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


#series_genre
#-------------
#Association table that establishes the many-to-many relationship between Series and Genre.
#Uses both foreign keys (genre.id and series.id) as a composite primary key.

#The relationship is accessed via series.genres, defined in the Series class using:
    #genres=db.relationship("Genre",secondary=series_genre,backref="series")

#The backref automatically creates the reverse relationship on Genre,
#allowing genre.series to return all series belonging to that genre.

series_genre=db.Table("series_genre",
                      db.Column("genre_id",db.Integer,db.ForeignKey("genre.id"),primary_key=True),
                      db.Column("series_id",db.Integer,db.ForeignKey("series.id"),primary_key=True))


class Series(db.Model):
    """
    Series
    --------
    Represents a TV series in the database.

    actors, creators: Stored as comma-separated strings rather than a Person table,
    as they are display-only fields that also feed into the RAG document for semantic search.

    poster_filename: Local filename, not a TMDB URL.

    source: Either "initial_scrape" (added during bulk ingestion) or "user_added" that is
    added dynamically when a user searched for it.

    status: Status of the series from TMDB. Only "Ended" shows are included in the initial scrape.
    Dynamically added shows may have other statuses.

    last_synced_at: Timestamp of last TMDB sync. Used for lazy refresh that is ongoing shows are
    re-synced when a user visits the series page and this timestamp is older than 7 days.

    tmdb_vote_average: Snapshot taken at ingestion time, not updated in real time.
    """

    __tablename__="series"
    id=db.Column(db.Integer,primary_key=True)
    tmdb_id=db.Column(db.Integer,unique=True,nullable=False)
    title=db.Column(db.String,nullable=False)
    description=db.Column(db.Text)
    origin_country=db.Column(db.String)
    first_air_date=db.Column(db.String)
    last_air_date=db.Column(db.String)
    actors=db.Column(db.String)
    creators=db.Column(db.String)
    tmdb_vote_average=db.Column(db.Float)
    num_seasons=db.Column(db.SmallInteger)
    num_eps=db.Column(db.Integer)
    poster_filename=db.Column(db.String)
    status=db.Column(db.String)
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
    """
    UserWatchEpisode
    -----------------
    This is going to be created automatically if the user ticks the show as watched and is deleted
    automatically when the user unticks it. its existence means the ep is watched by the user.
    """

    __tablename__="user_watch_episode"
    ep_id=db.Column(db.Integer,db.ForeignKey("episode.id"),primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"), primary_key=True)
    watched_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))


class UserSeriesRating(db.Model):
    """
    UserSeriesRating
    -----------------
    Needed for the user to be able to rate or takes notes regarding the series.
    As they can do and skip the other, neither one of them is non-nullable.
    """
    __tablename__="user_series_rating"
    series_id=db.Column(db.Integer,db.ForeignKey("series.id"),primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),primary_key=True)
    rating=db.Column(db.Float)
    notes=db.Column(db.Text)
    created_at=db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))