import os


class Config:
    SECRET_KEY = os.environ.get("SIDH_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SIDH_SQLALCHEMY_DATABASE_URI")
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("SIDH_EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("SIDH_EMAIL_PASS")

