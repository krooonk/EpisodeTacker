from flask import Flask
from models import db
import os
from datetime import datetime
import pycountry

def format_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%B %d, %Y")
    except:
        return value

def format_country(value):
    try:
        codes=[c.strip() for c in value.split(",")]
        names=[]
        for code in codes:
            country=pycountry.countries.get(alpha_2=code)
            name=getattr(country, 'common_name', None) or country.name
            names.append(name if country else code)
        return ", ".join(names)
    except:
        return value

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app=Flask(__name__, instance_path=os.path.join(ROOT, "instance"))

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///episodetracker.db"
db.init_app(app)

app.jinja_env.filters["format_date"]=format_date
app.jinja_env.filters["format_country"]=format_country

from episodeTrackerApp import routes
