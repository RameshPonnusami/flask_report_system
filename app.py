from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,session
from flask_sqlalchemy import Model, SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager

app = Flask(__name__)

app.config.from_object('config.DevConfig')
#if 'SECRET_KEY' not in app.config:


app.config['SECRET_KEY']='ThisIsFlaskGraphene'
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
app.config['SESSION_TYPE'] = 'filesystem'

engine = create_engine(db_uri, convert_unicode=True)
# Declarative base model to create database tables and classes
Base = declarative_base()
Base.metadata.bind = engine  # Bind engine to metadata of the base class
# Create database session object
db_session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base.query = db_session.query_property()  # Used by graphql to execute queries


from sqlalchemy import MetaData

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(app,metadata=MetaData(naming_convention=naming_convention))



migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


