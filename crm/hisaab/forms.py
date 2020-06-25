from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField, validators
from wtforms.validators import DataRequired


class HisaabForm(FlaskForm):
    opening = IntegerField("Opening", validators=[DataRequired()])
    manual_trans = IntegerField("Manual Transfer", validators=[validators.Optional()])
    auto_trans = IntegerField("Auto Transfer", validators=[validators.Optional()])
    closing = IntegerField("Closing", validators=[DataRequired()])
    last_debt = IntegerField("Last Debt", validators=[validators.Optional()])
    amt_received = IntegerField("Amount Paying", validators=[DataRequired()])
    remarks = TextAreaField("Remarks", validators=[validators.Optional()])
    submit = SubmitField("Calculate")
