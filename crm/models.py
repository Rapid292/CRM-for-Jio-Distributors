from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from crm import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from flask import current_app


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

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

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
    calc_master_bal = db.Column(db.Integer, nullable=False, default=0)
    master_diff = db.Column(db.Integer, nullable=False, default=0)
    remarks = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Master('{self.closing}', '{self.open_bal}', '{self.date}', '{self.remarks}')"
