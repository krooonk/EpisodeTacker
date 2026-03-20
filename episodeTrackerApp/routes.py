from episodeTrackerApp import app
from flask import render_template,request
from models import Series,Genre

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/series")
def series_page():
    genres=Genre.query.all()
    selected_genres=request.args.getlist("genre",type=int)
    query=Series.query
    if selected_genres:
        query=query.filter(Series.genres.any(Genre.id.in_(selected_genres)))
    page=request.args.get("page",1,type=int)
    sorting=request.args.get("sort","rating")
    if sorting=="title":
        query=query.order_by(Series.title.asc())
    elif sorting=="most_episodes":
        query=query.order_by(Series.num_eps.desc())
    elif sorting=="fewest_episodes":
        query=query.order_by(Series.num_eps.asc())
    else:
        query=query.order_by(Series.tmdb_vote_average.desc())
    series=query.paginate(page=page,per_page=24)
    return render_template("series.html",series=series,genres=genres,selected_genres=selected_genres,sorting=sorting)

@app.route("/series/<int:id>")
def series_detailed_page(id):
    series=Series.query.get_or_404(id)
    return render_template("series_detailed.html",series=series)