import os


class Config:
   SECRET_KEY = "e9e14493faed51435c3011ba8cbc61b1"
   SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
   MAIL_SERVER = "smtp.googlemail.com"
   MAIL_PORT = 587
   MAIL_USE_TLS = True
   MAIL_USERNAME = os.environ.get("EMAIL_USER")
   MAIL_PASSWORD = os.environ.get("EMAIL_PASS")