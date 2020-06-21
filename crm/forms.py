from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    IntegerField,
    TextAreaField,
    validators,
)
from wtforms.validators import DataRequired, Length, email, EqualTo, ValidationError
from crm.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), email()])
    pos_id = IntegerField("POS ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")

    def validate_pos_id(self, pos_id):
        user = User.query.filter_by(pos_id=pos_id.data).first()
        if user:
            raise ValidationError(
                f"{pos_id.data} is already registered under username {user.username}. Please choose a different one."
            )


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class UpdateProfileForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), email()])
    pos_id = IntegerField("POS ID", validators=[DataRequired()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "jpeg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )

    def validate_pos_id(self, pos_id):
        if pos_id.data != current_user.pos_id:
            user = User.query.filter_by(pos_id=pos_id.data).first()
            if user:
                raise ValidationError(
                    f"{pos_id.data} is already registered under username {user.username}. Please choose a different one."
                )


class HisaabForm(FlaskForm):
    opening = IntegerField("Opening", validators=[DataRequired()])
    manual_trans = IntegerField("Manual Transfer", validators=[validators.Optional()])
    auto_trans = IntegerField("Auto Transfer", validators=[validators.Optional()])
    closing = IntegerField("Closing", validators=[DataRequired()])
    last_debt = IntegerField("Last Debt", validators=[validators.Optional()])
    amt_received = IntegerField("Amount Paying", validators=[DataRequired()])
    remarks = TextAreaField("Remarks", validators=[validators.Optional()])
    submit = SubmitField("Calculate")


class MasterForm(FlaskForm):
    opening = IntegerField("Opening", validators=[DataRequired()])
    primary = IntegerField("Primary", validators=[validators.Optional()])
    manual_trans = IntegerField("Manual Transfer", validators=[validators.Optional()])
    auto_trans = IntegerField("Auto Transfer", validators=[validators.Optional()])
    fos_bal = IntegerField("FOS Balance", validators=[DataRequired()])
    master_bal = IntegerField("Master Balance", validators=[DataRequired()])
    remarks = TextAreaField("Remarks", validators=[validators.Optional()])
    submit = SubmitField("Calculate")
