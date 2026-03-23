from flask import Flask,flash,redirect
from models import db,User
import os
from datetime import datetime,timedelta
import pycountry
from flask_login import LoginManager
from dotenv import load_dotenv
load_dotenv()
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
app=Flask(__name__, instance_path=os.path.join(ROOT,"instance"))

app.config["SECRET_KEY"]=os.getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"]=timedelta(days=10)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///episodetracker.db"
db.init_app(app)

app.jinja_env.filters["format_date"]=format_date
app.jinja_env.filters["format_country"]=format_country

login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

bcrypt=Bcrypt(app)

limiter=Limiter(get_remote_address,app=app,default_limits=[])

#for too many requests
@app.errorhandler(429)
def rate_limit_handler(e):
    flash("Too many login attempts. Please try later.",category="danger")
    return redirect("/")

from episodeTrackerApp import routes
