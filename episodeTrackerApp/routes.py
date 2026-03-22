from episodeTrackerApp import app,bcrypt
from flask import render_template,request,url_for,flash,redirect
from models import Series,Genre,User,db
from episodeTrackerApp.forms import RegistrationForm
from flask_login import login_user

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

@app.route("/search")
def search_page():
    q=request.args.get("q", "")
    page=request.args.get("page", 1, type=int)
    if not q:
        series=[]
    else:
        query=Series.query.filter(Series.title.ilike(f"{q}%") | Series.title.ilike(f"% {q}%"))
        series=query.paginate(page=page, per_page=24)

    return render_template("search.html",series=series,q=q)

@app.route("/register",methods=["POST","GET"])
def register_page():
    form=RegistrationForm(request.form)
    if request.method=="POST" and form.validate():
        new_user=User(
            username=form.username.data,
            email=form.email.data,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Account created successfully!",category="success")
        return redirect(url_for("home_page"))
    elif request.method=="POST":
        if form.errors:
            for err_msg in form.errors.values():
                flash(f"There was an error:{err_msg}",category="danger")
    return render_template("register.html",form=form)

@app.route("/login",methods=["POST","GET"])
def login_page():
    pass