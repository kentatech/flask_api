import secrets
import os
class Base:
    SECRET_KEY = secrets.token_hex(16)
class Development(Base):
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_ENV= os.getenv("FLASK_ENV")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") 
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

