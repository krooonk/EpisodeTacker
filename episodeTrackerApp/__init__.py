from flask import Flask
from models import db
import os

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app=Flask(__name__, instance_path=os.path.join(ROOT, "instance"))

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///episodetracker.db"
db.init_app(app)

from episodeTrackerApp import routes
