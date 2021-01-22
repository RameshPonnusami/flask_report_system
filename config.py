"""Flask config."""
import os
#from os import environ, path
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

db_name = 'database.db'
db_path = os.path.join(os.path.dirname(__file__), db_name)
print(db_path)
# db_uri= 'sqlite:///database.db'

db_uri= 'sqlite:///flask_report_system.db'
#db_uri = 'postgresql://postgres:***@localhost:5432/flask_report'
print(db_uri)

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ.get('PROD_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevConfig(Config):
    print('development server running')
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI =db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS=True
   # SQLALCHEMY_TRACK_MODIFICATIONS = False

