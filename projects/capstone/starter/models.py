import os
from sqlalchemy import Column, String, Integer, create_engine, Date
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "casting_agency"
# database_path = "postgres://{}/{}".format('localhost:5432', database_name)
database_path = "postgres://jzqanyoljeufxj:ae406e0f7d35eff8aaa8253ea8098c34bb804e7c1db96654611c1fe19a628eda@ec2-52-202-66-191.compute-1.amazonaws.com:5432/deea4cjsf7gkun"
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    '''
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    '''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_drop_and_create_all():
    '''
    db_drop_and_create_all()
        drops the database tables and starts fresh
        can be used to initialize a clean database
        !!NOTE you can change the database_filename variable
        to have multiple verisons of a database
    '''
    db.drop_all()
    db.create_all()


class Actor(db.Model):
    '''
    Actor
    '''
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }


class Movie(db.Model):
    '''
    Movie
    '''
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(String)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }
