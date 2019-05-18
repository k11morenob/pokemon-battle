from flask_pymongo import PyMongo
from resources import app

db = PyMongo(app).db