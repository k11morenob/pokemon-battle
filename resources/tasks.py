from resources import celery
from db import db

@celery.task(bind=True)
def create_league(self, data):
	db.leagues.insert({'name': data['name']})

