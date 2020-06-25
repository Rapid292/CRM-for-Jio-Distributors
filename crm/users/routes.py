from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_user, logout_user, login_required
from crm.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateProfileForm,
    RequestResetForm,
    ResetPasswordForm,
)
from crm.users.utils import save_picture, send_reset_email
from crm.models import User, Hisaab
from crm import bcrypt, db, admin

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
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
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register Now", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Sign In", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@users.route("/profile", methods=["GET", "POST"])
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
        return redirect(url_for("users.profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.pos_id.data = current_user.pos_id
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "profile.html", title="Profile", image_file=image_file, form=form
    )


@users.route("/home/user/<string:username>")
@login_required
def user_hisaab(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    hisaab = (
        Hisaab.query.filter_by(fos=user)
        .order_by(Hisaab.date.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template(
        "user_hisaab.html",
        title=current_user.username + " Report",
        hisaab=hisaab,
        admin=admin,
        user=user,
    )


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password", "info")
        return redirect(url_for("users.login"))

    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if not user:
        flash("This is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash(
            "Hey! Your password has been updated! You are now able to log in", "success"
        )
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
