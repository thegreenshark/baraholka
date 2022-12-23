from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import datetime
import psycopg2
from werkzeug.utils import secure_filename
import os
import uuid
import math
from PIL import Image
import hashlib
from enum import Enum


ALLOWED_FILE_TYPES = {'png', 'jpg', 'jpeg', 'bmp'}
PASSWORD_SALT1 = 'FA3YVNgG'
PASSWORD_SALT2 = '2dN4T5NK'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'baraholka/static/userFiles/'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 #32 мб
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

dbCon = psycopg2.connect(database="baraholka", user="baraholkaapp", password="test1234", host="localhost", port=5432)
dbCur = dbCon.cursor()

app.secret_key = 'idk just some random shit i guess'

import baraholka.routes