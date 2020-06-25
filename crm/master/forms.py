from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField, validators
from wtforms.validators import DataRequired


class MasterForm(FlaskForm):
    opening = IntegerField("Opening", validators=[DataRequired()])
    primary = IntegerField("Primary", validators=[validators.Optional()])
    manual_trans = IntegerField("Manual Transfer", validators=[validators.Optional()])
    auto_trans = IntegerField("Auto Transfer", validators=[validators.Optional()])
    fos_bal = IntegerField("FOS Balance", validators=[DataRequired()])
    master_bal = IntegerField("Master Balance", validators=[DataRequired()])
    remarks = TextAreaField("Remarks", validators=[validators.Optional()])
    submit = SubmitField("Calculate")
