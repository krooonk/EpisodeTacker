from episodeTrackerApp import app
from flask import render_template

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/series")
def series_page():
    return render_template("series.html")