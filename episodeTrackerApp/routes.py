from episodeTrackerApp import app,bcrypt,limiter
from flask import render_template,request,url_for,flash,redirect,session
from models import Series,Genre,User,db
from episodeTrackerApp.forms import RegistrationForm,LoginForm
from flask_login import login_user,logout_user

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
            for err_msg_field in form.errors.values():
                for err_msg in err_msg_field:
                    flash(f"{err_msg}",category="danger")
    return render_template("register.html",form=form)

@app.route("/login",methods=["POST","GET"])
@limiter.limit("5 per minute;20 per hour;50 per day")
def login_page():
    form=LoginForm(request.form)
    if request.method=="POST" and form.validate():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        attempted_password=False
        if attempted_user:
            attempted_password=bcrypt.check_password_hash(attempted_user.password_hash,form.password.data)
        if attempted_password:
            login_user(attempted_user,remember=form.remember_me.data)
            session.permanent=True
            flash(f"Hi,{attempted_user.username}!", category="success")
            return redirect(url_for("home_page"))
        else:
            flash("User and password do not match. Please try again.",category="danger")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have logged out!",category="info")
    return redirect(url_for("home_page"))