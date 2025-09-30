import secrets
import os
class Base:
    SECRET_KEY = secrets.token_hex(16)
class Development(Base):
    FLASK_APP = os.environ.get("main.py")
    FLASK_ENV= os.environ.get("development")
    POSTGRES_USER = os.environ.get("POSTGRES")
    POSTGRES_PASSWORD = os.environ.get("NEWPAS4u.")
    POSTGRES_DB = os.environ.get("flask_api")

