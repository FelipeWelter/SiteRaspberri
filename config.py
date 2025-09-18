import os

SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta")
SQLALCHEMY_DATABASE_URI = "sqlite:///../instance/site.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
