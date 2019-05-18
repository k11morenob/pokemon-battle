from resources import celery
from db import db
from .utils import get_pokemon, get_pokemon_move, get_accuracy, random_pokemons, battle
from bson.objectid import ObjectId
from bson.errors import InvalidId
import random

@celery.task(bind=True)
def create_league(self, data):
	db.leagues.insert({'name': data['name']})

@celery.task(bind=True)
def create_master(self, data):
	pokemons = random_pokemons(data['n_pokemons'])
	master = db.masters.insert({'name': data['name'], 'pokemons': pokemons, 'league':data['league'], 'battles_won': 0, 'battles_lost': 0})

@celery.task(bind=True)
def update_master(self, mid, data):
	db.masters.update_one({'_id': ObjectId(mid) }, {"$set":data})

@celery.task(bind=True)
def lg_battle(self, data):

	masters = db.masters.find({ '_id': { '$in': [ ObjectId(data['master_1']), ObjectId(data['master_2']) ] } })
	result = {'winner': None, 'loser': None, 'league': masters[0]['league']}

	current_battle = battle(masters)

	result['winner'] = current_battle['winner']
	result['loser'] = current_battle['loser']

	winner = db.masters.find_one({'_id': ObjectId(result['winner']) })

	try:
		winner_count = winner['battles_won']
	except KeyError:
		winner_count = 0

	update_master.delay(result['winner'], {'battles_won': winner_count + 1})

	loser = db.masters.find_one({'_id': ObjectId(result['loser']) })

	try:
		loser_count = loser['battles_lost']
	except KeyError:
		loser_count = 0
	
	update_master.delay(result['loser'], {'battles_lost': loser_count + 1})

	db.league_battles.insert(result)

@celery.task(bind=True)
def training_battle(self, data):


	masters = db.masters.find({ '_id': { '$in': [ ObjectId(data['master_1']), ObjectId(data['master_2']) ] } })
	result = {'winner': None, 'loser': None}

	current_battle = battle(masters)

	result['winner'] = current_battle['winner']
	result['loser'] = current_battle['loser']

	db.training_battles.insert(result)