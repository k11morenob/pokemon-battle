from flask_restplus import Resource
from restplus import api
from datetime import datetime, timedelta, time
from celery.result import AsyncResult
from celery.task.control import revoke
from flask import request
from db import db
import json
from flask import jsonify
from bson.objectid import ObjectId
from bson.errors import InvalidId
import random
from .utils import get_pokemon
from .tasks import *

ns = api.namespace('league', description='Endpoint for leagues')

league_parser = api.parser()
league_parser.add_argument('name', type=str, help='name of your league', location='form', required=True)

@ns.route('/')

class leagues(Resource):

	def get(self):
		response = []
		try:
			leagues = db.leagues.find()
			for league in leagues:
				response.append({'id': str(league.get('_id')), 'name': league['name']})
			return jsonify(response)
		except Exception as e:
			return jsonify({'error' : str(e)})
	
	@api.doc(parser=league_parser)
	@api.expect(league_parser)
	def post(self):
		args = league_parser.parse_args()
		create_league(args)
		return {'message': 'request success'}

@ns.route('/<string:lid>')

class league(Resource):
	
	def get(self, lid):
		try:
			league = db.leagues.find_one({'_id': ObjectId(lid) })
			if league == None:
				api.abort(400, 'league not found')
			response = {'id': str(league.get('_id')), 'name': league['name']}
			return jsonify(response)
		except InvalidId as e:
			api.abort(400, e)

	@api.doc(parser=league_parser)
	@api.expect(league_parser)
	def put(self, lid): 
		args = league_parser.parse_args()
		db.leagues.update_one({'_id': ObjectId(lid) }, {"$set":{'name': args['name']}})
		league = db.leagues.find_one({'_id': ObjectId(lid) })
		return jsonify({'id': str(league.get('_id')), 'name': league['name']})



ns = api.namespace('masters', description='Endpoint for leagues')

master_parser = api.parser()
master_parser.add_argument('league', type=str, help="league's id", location='form', required=True)
master_parser.add_argument('name', type=str, help="master's name", location='form', required=True)
master_parser.add_argument('n_pokemons', type=int, help="number of pokemons", location='form', required=True)

@ns.route('/')

class masters(Resource):

	def get(self):
		response = []
		try:
			masters = db.masters.find()
			for master in masters:
				response.append({'id': str(master.get('_id')), 'name': master['name'], 'pokemons': master['pokemons'], 'league': master['league']})
			return jsonify(response)
		except Exception as e:
			return jsonify({'error' : str(e)})

	@api.doc(parser=master_parser)
	@api.expect(master_parser)
	def post(self):
		args = master_parser.parse_args()
		self.validate(args)
		pokemons = self.get_pokemons(args['n_pokemons'])
		master = db.masters.insert({'name': args['name'], 'pokemons': pokemons, 'league':args['league']})
		new_master = db.masters.find_one({'_id': master })
		response = {'id': str(new_master.get('_id')), 'name': new_master['name'], 'pokemons': new_master['pokemons'], 'league': new_master['league']}
		return response

	def validate_league(self, lid):
		try:
			league = db.leagues.find_one({'_id': ObjectId(lid) })
			if league == None:
				api.abort(400, 'league not found')
			return
		except InvalidId as e:
			api.abort(400, e)

	def validate(self, data):

		self.validate_league(data['league'])

		return 

	def get_pokemons(self, n_pokemons):

		pokemons_ids = []
		pokemons = []
		while True:
			new_pokemon = random.randint(1,101)
			
			if len(pokemons_ids) >= n_pokemons:
				break
			
			try:
				pokemons_ids.index(new_pokemon)
			except ValueError:
				pokemons_ids.append(new_pokemon)

		for pkid in pokemons_ids:
			pokemon = get_pokemon(pkid)
			pokemons.append(json.loads(pokemon)['name'])

		return pokemons

ns = api.namespace('league', description='Endpoint for battles')

battle_parser = api.parser()
battle_parser.add_argument('master_1', type=str, help="master 1 id", location='form', required=True)
battle_parser.add_argument('master_2', type=str, help="master 2 id", location='form', required=True)

@ns.route('/battle')

class league_battle(Resource):

	@api.doc(parser=battle_parser)
	@api.expect(battle_parser)
	def post(self):
		pass