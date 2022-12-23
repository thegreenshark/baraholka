from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import datetime
import psycopg2
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
import uuid
import math
from PIL import Image
import hashlib
from enum import Enum
import json


SETTINGS_FILE_NAME = './settings.json'

jsonFile_r = open(SETTINGS_FILE_NAME, 'r', encoding = 'utf-8')
appSettings = json.load(jsonFile_r)
jsonFile_r.close()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'baraholka/static/userFiles/'
app.config['MAX_CONTENT_LENGTH'] = appSettings['maxContentLengthMb'] * 1024 * 1024 #перевод в байты
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

dbCon = psycopg2.connect(database = appSettings['dbName'], user = appSettings['dbUsername'], password = appSettings['dbPassword'], host = appSettings['dbHost'], port = appSettings['dbPort'])
dbCur = dbCon.cursor()

app.secret_key = appSettings['appSecretKey']

import baraholka.routes