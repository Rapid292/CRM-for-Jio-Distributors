from flask import Blueprint, render_template
from flask_login import login_required
from crm.models import Hisaab, User, Master
from crm import db, admin

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", title="Index", admin=admin)


@main.route("/home")
@login_required
def home():
    fos = User.query.all()
    return render_template(
        "home.html",
        title="Home",
        fos=fos,
        Hisaab=Hisaab,
        admin=admin,
        Master=Master,
        db=db,
    )


@main.route("/about")
def about():
    return render_template("about.html", title="About")
