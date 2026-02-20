"""
populate_db.py
--------------
Loads initial_ingest.json and populates the SQLite database with series, seasons,
episodes, and genres.
Run once after create_db.py on a fresh database.
"""

import json
from flask import Flask
from models import db, Genre, Series, Season, Episode
import os

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app=Flask(__name__, instance_path=os.path.join(ROOT, "instance"))

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///episodetracker.db"

db.init_app(app)

with app.app_context():

    with open("initial_ingest.json","r") as f:
        db_json=json.load(f)

    genres=db_json["genres"]
    for genre in genres:
        new_genre=Genre(tmdb_id=genre["id"],name=genre["name"])
        db.session.add(new_genre)
    db.session.commit()
    print("Genres inserted.")

    shows=db_json["shows"]
    count=0
    for show in shows:

        show_genres=Genre.query.filter(Genre.tmdb_id.in_(show["genres"])).all()

        new_series=Series(
            tmdb_id=show["tmdb_id"],
            title=show["title"],
            description=show["description"],
            origin_country=show["origin_country"],
            first_air_date=show["first_air_date"],
            last_air_date=show["last_air_date"],
            actors=show["actors"],
            creators=show["creators"],
            tmdb_vote_average=show["tmdb_vote_average"],
            num_seasons=show["num_seasons"],
            num_eps=show["num_eps"],
            poster_filename=show["poster_filename"],
            status=show["status"],
            genres=show_genres
        )
        db.session.add(new_series)
        db.session.flush() #so we can use the autogenerate id for series
        seasons=show["seasons"]
        for season in seasons:
            new_season=Season(
                series_id=new_series.id,
                season_number=season["season_number"],
                num_eps=season["episode_count"]
            )
            db.session.add(new_season)
            db.session.flush()

            for episode in season["episodes"]:
                new_episode=Episode(
                    season_id=new_season.id,
                    episode_number=episode["episode_number"],
                    title=episode["title"],
                    description=episode["description"]
                )
                db.session.add(new_episode)
        db.session.commit()
        count+=1
        if count%50==0:
            print(f"Inserted {count} shows.")

    print(f"Inserted {count} shows.")