import secrets
import os
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from crm.forms import (
    RegistrationForm,
    LoginForm,
    UpdateProfileForm,
    HisaabForm,
    MasterForm,
)
from crm.models import Hisaab, User, Master
from crm import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required

admin = "Admin"


@app.route("/")
def index():
    return render_template("index.html", title="Index")


@app.route("/home")
@login_required
def home():
    fos = User.query.all()
    hisaab = Hisaab.query.filter()

    return render_template(
        "home.html", title="Home", fos=fos, hisaab=hisaab, admin=admin
    )


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data,
            pos_id=form.pos_id.data,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        flash(
            f"Hey! Your account has been created { form.username.data }!, Log In Now!!",
            "success",
        )
        return redirect(url_for("login"))
    return render_template("register.html", title="Register Now", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.split(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    output_size = (175, 175)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.pos_id = form.pos_id.data
        db.session.commit()
        flash("Your profile has been updated", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.pos_id.data = current_user.pos_id
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "profile.html", title="Profile", image_file=image_file, form=form
    )


def cal_total_transfer(manual, auto):
    total_transfer = manual + auto
    return total_transfer


def cal_total_sale(opening, total_trans, closing):
    total = opening + total_trans - closing
    return total


def cal_comm_value(total_sale, comm=4):
    commission = round(total_sale * (comm / 100))
    return commission


def cal_net_sale(total_sale, comm_value):
    net_sale = total_sale - comm_value
    return net_sale


def cal_latest_debt(net_sale, last_debt, amt_received):
    latest_debt = net_sale + last_debt - amt_received
    return latest_debt


@app.route("/home/hisaab", methods=["GET", "POST"])
@login_required
def hisaab():
    form = HisaabForm()

    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)
        total_sale = cal_total_sale(
            (form.opening.data), total_trans, (form.closing.data)
        )
        comm_value = cal_comm_value(total_sale)
        net_sale = cal_net_sale(total_sale, comm_value)
        latest_debt = cal_latest_debt(
            net_sale, (form.last_debt.data), (form.amt_received.data)
        )

        hisaab = Hisaab(
            open_bal=form.opening.data,
            manual_trans=form.manual_trans.data,
            auto_trans=form.auto_trans.data,
            closing=form.closing.data,
            total_trans=total_trans,
            total_sale=total_sale,
            commission_value=comm_value,
            net_sale=net_sale,
            last_debt=form.last_debt.data,
            amt_received=form.amt_received.data,
            latest_debt=latest_debt,
            remarks=form.remarks.data,
            fos=current_user,
        )

        db.session.add(hisaab)
        db.session.commit()

        flash("Your report has been generated", "success")
        return redirect(url_for("report"))
    return render_template(
        "hisaab.html", title="Hisaab", form=form, legend="New Hisaab"
    )


@app.route("/home/hisaab/report")
@login_required
def report():
    page = request.args.get("page", 1, type=int)
    hisaab = Hisaab.query.order_by(Hisaab.date.desc()).paginate(page=page, per_page=10)
    return render_template("report.html", title="Report", hisaab=hisaab, admin=admin)


@app.route("/home/hisaab/report/<int:hisaab_id>")
@login_required
def single_hisaab(hisaab_id):
    hisaab = Hisaab.query.get_or_404(hisaab_id)
    return render_template(
        "single_hisaab.html", title=hisaab.date, hisaab=hisaab, admin=admin
    )


@app.route("/home/hisaab/report/<int:hisaab_id>/update", methods=["GET", "POST"])
@login_required
def update_hisaab(hisaab_id):

    hisaab = Hisaab.query.get_or_404(hisaab_id)
    if current_user.username != admin:
        abort(403)
    form = HisaabForm()
    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)
        total_sale = cal_total_sale(
            (form.opening.data), total_trans, (form.closing.data)
        )
        comm_value = cal_comm_value(total_sale)
        net_sale = cal_net_sale(total_sale, comm_value)
        latest_debt = cal_latest_debt(
            net_sale, (form.last_debt.data), (form.amt_received.data)
        )
        hisaab.date = datetime.now()
        hisaab.open_bal = form.opening.data
        hisaab.manual_trans = form.manual_trans.data
        hisaab.auto_trans = form.auto_trans.data
        hisaab.closing = form.closing.data
        hisaab.total_trans = total_trans
        hisaab.total_sale = total_sale
        hisaab.commission_value = comm_value
        hisaab.net_sale = net_sale
        hisaab.last_debt = form.last_debt.data
        hisaab.amt_received = form.amt_received.data
        hisaab.latest_debt = latest_debt
        hisaab.remarks = form.remarks.data
        db.session.commit()
        flash("Your hisaab has been updated", "success")
        return redirect(url_for("single_hisaab", hisaab_id=hisaab_id))
    elif request.method == "GET":
        form.opening.data = hisaab.open_bal
        form.manual_trans.data = hisaab.manual_trans
        form.auto_trans.data = hisaab.auto_trans
        form.closing.data = hisaab.closing
        form.last_debt.data = hisaab.last_debt
        form.amt_received.data = hisaab.amt_received
        form.remarks.data = hisaab.remarks
    return render_template(
        "hisaab.html",
        title="Update Hisaab",
        hisaab=hisaab,
        admin=admin,
        form=form,
        legend="Update Hisaab",
    )


@app.route("/home/hisaab/report/<int:hisaab_id>/delete", methods=["POST"])
@login_required
def delete_hisaab(hisaab_id):
    hisaab = Hisaab.query.get_or_404(hisaab_id)
    if current_user.username != admin:
        abort(403)
    db.session.delete(hisaab)
    db.session.commit()
    flash("Your hisaab has been deleted!", "success")
    return redirect(url_for("report"))


@app.route("/home/master", methods=["GET", "POST"])
@login_required
def master():
    form = MasterForm()

    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)

        master = Master(
            open_bal=form.opening.data,
            primary=form.primary.data,
            manual_trans=form.manual_trans.data,
            auto_trans=form.auto_trans.data,
            closing=form.closing.data,
            total_trans=total_trans,
            fos_bal=form.fos_bal.data,
            master_bal=form.master_bal.data,
            remarks=form.remarks.data,
        )

        db.session.add(master)
        db.session.commit()

        flash("Your report has been generated", "success")
        return redirect(url_for("master_report"))
    return render_template("master.html", title="Master", form=form, admin=admin)


@app.route("/home/master/master_report")
@login_required
def master_report():
    master = Master.query.order_by(Master.date.desc())
    return render_template(
        "master_report.html", title="Report", master=master, admin=admin
    )


@app.route("/home/user/<string:username>")
@login_required
def user_hisaab(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    hisaab = (
        Hisaab.query.filter_by(fos=user)
        .order_by(Hisaab.date.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template(
        "user_hisaab.html", title="Hisaab Report", hisaab=hisaab, admin=admin, user=user
    )

