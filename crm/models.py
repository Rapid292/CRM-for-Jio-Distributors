from crm import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpeg")
    password = db.Column(db.String(20), nullable=False)
    pos_id = db.Column(db.Integer, unique=True, nullable=False)
    hisaab = db.relationship("Hisaab", backref="fos", lazy="dynamic")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.pos_id}')"


class Hisaab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    open_bal = db.Column(db.Integer, nullable=False, default=0)
    manual_trans = db.Column(db.Integer, nullable=False, default=0)
    auto_trans = db.Column(db.Integer, nullable=False, default=0)
    closing = db.Column(db.Integer, nullable=False, default=0)
    total_trans = db.Column(db.Integer, default=0)
    total_sale = db.Column(db.Integer, default=0)
    commission_value = db.Column(db.Integer, default=0)
    net_sale = db.Column(db.Integer, default=0)
    last_debt = db.Column(db.Integer, nullable=False, default=0)
    amt_received = db.Column(db.Integer, nullable=False, default=0)
    latest_debt = db.Column(db.Integer, default=0)
    remarks = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Hisaab('{self.closing}', '{self.open_bal}', '{self.date}', '{self.remarks}')"


class Master(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    open_bal = db.Column(db.Integer, nullable=False, default=0)
    primary = db.Column(db.Integer, nullable=False, default=0)
    manual_trans = db.Column(db.Integer, nullable=False, default=0)
    auto_trans = db.Column(db.Integer, nullable=False, default=0)
    closing = db.Column(db.Integer, nullable=False, default=0)
    total_trans = db.Column(db.Integer, default=0)
    fos_bal = db.Column(db.Integer, default=0)
    master_bal = db.Column(db.Integer, nullable=False, default=0)
    remarks = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Master('{self.closing}', '{self.open_bal}', '{self.date}', '{self.remarks}')"
