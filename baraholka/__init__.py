from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import datetime
import psycopg2

app = Flask(__name__)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

dbCon = psycopg2.connect(database="baraholka", user="baraholkaapp", password="test1234", host="localhost", port=5432)
dbCur = dbCon.cursor()


app.secret_key = 'idk just some random shit i guess'


class User(UserMixin):
    id = None
    email = None
    password = None
    firstname = None
    lastname = None
    phone = None
    isModerator = None

    def get_id(self = None):
        return User.id


    @property
    def is_active(self):
        return self.is_active

    @property
    def is_authenticated(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return self.is_anonymous


    @staticmethod
    @login_manager.user_loader
    def loadById(id):
        dbCur.execute(f"SELECT * FROM appuser WHERE id = '{id}'")
        result = dbCur.fetchone()

        if result is None:
            User.id = None
            User.email = None
            User.password = None
            User.firstname = None
            User.lastname = None
            User.phone = None
            User.isModerator = None

            return None

        else:
            User.id = result[0]
            User.email = result[1]
            User.password = result[2]
            User.firstname = result[3]
            User.lastname = result[4]
            User.phone = result[5]
            User.isModerator = result[6]

            return User

import baraholka.routes