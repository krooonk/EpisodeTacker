from episodeTrackerApp import app
from flask import render_template,request
from models import Series

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/series")
def series_page():
    page=request.args.get("page",1,type=int)
    series=Series.query.paginate(page=page,per_page=24)
    return render_template("series.html",series=series)
