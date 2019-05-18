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
		create_league.delay(args)
		return {'message': 'request success'}

@ns.route('/<string:lid>')
@ns.doc(params={'lid': 'Id of the league'})
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

battle_parser = api.parser()
battle_parser.add_argument('master_1', type=str, help="master 1 id", location='form', required=True)
battle_parser.add_argument('master_2', type=str, help="master 2 id", location='form', required=True)

@ns.route('/battle')

class league_battle(Resource):

	@api.doc(parser=battle_parser)
	@api.expect(battle_parser)
	def post(self):
		args = battle_parser.parse_args()
		self.validate(args)
		data = {'master_1': args['master_1'], 'master_2': args['master_2']}
		lg_battle.delay(data)
		return {'message': 'league battle is in process'}

	def validate(self, data):
		if data['master_1'] == data['master_2']:
			api.abort(400, "you can't battle against yourself")
		try:
			masters = db.masters.find({ '_id': { '$in': [ ObjectId(data['master_1']), ObjectId(data['master_2']) ] } })
			if masters[0]['league'] != masters[1]['league']:
				api.abort(400, "the masters don't belong to the same league")
		except InvalidId as e:
			api.abort(400, e)


@ns.route('/rank/<string:lid>')
@ns.doc(params={'lid': 'Id of the league'})
class rank(Resource):

	def get(self, lid):
		rank = {}
		position = 1
		league_masters = db.masters.find({'league': lid}).sort('battles_won', -1)
		for master in league_masters:
			rank[position] = {'id': str(master['_id']),'name': master['name'], 'victories': master.get('battles_won') or 0, 'defeats': master.get('battles_lost') or 0}
			position = position + 1
		return rank

@ns.route('/results/<string:lid>')
@ns.doc(params={'lid': 'Id of the league'})
class league_results(Resource):

	def get(self, lid):
		result = {}
		league = db.leagues.find_one({ '_id': ObjectId(lid)})
		result['league'] = {'id':lid, 'name': league['name']}
		result['results'] = []
		battles = db.league_battles.find({'league': lid})
		for battle in battles:
			winner = db.masters.find_one({'_id': ObjectId(battle['winner'])})
			loser = db.masters.find_one({'_id': ObjectId(battle['loser'])})
			result['results'].append(
					{
					'winner': 
						{
							'id': str(winner['_id']),
							'name': winner['name']
						}
					,
					'loser': 
						{
							'id': str(loser['_id']),
							'name': loser['name']
						}
					})
		return result

@ns.route('/winners')

class winners(Resource):

	def get(self):
		response = []
		leagues = db.leagues.find()
		for league in leagues:
			try:
				winner = db.masters.find({'league': str(league['_id'])}).sort('battles_won', -1).limit(1)[0]
				if winner.get('battles_won') != None and winner.get('battles_won') > 0:
					response.append({'league':{'id': str(league['_id']), 'name':league['name']},'winner': {'id': str(winner['_id']),'name': winner['name'], 'victories': winner.get('battles_won') or 0, 'defeats': winner.get('battles_lost') or 0}})
				else:
					response.append({'league': {'id': str(league['_id']), 'name':league['name']} ,'winner': {}})
			except IndexError:
				response.append({'league':{'id': str(league['_id']), 'name':league['name']},'winner': {}})

		return response


ns = api.namespace('masters', description='Endpoint for masters')

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
				response.append({'id': str(master.get('_id')), 'name': master['name'], 'pokemons': master['pokemons'], 'league': master['league'], 'battles_won': master.get('battles_won'), 'battles_lost': master.get('battles_lost')})
			return jsonify(response)
		except Exception as e:
			return jsonify({'error' : str(e)})

	@api.doc(parser=master_parser)
	@api.expect(master_parser)
	def post(self):
		args = master_parser.parse_args()
		self.validate(args)
		create_master.delay(args)
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

		if data['n_pokemons'] < 1 or data['n_pokemons'] > 6:
			api.abort(400, 'Number of pokemons has to be between 1 and 6')			
		self.validate_league(data['league'])

		return

ns = api.namespace('training', description='Endpoint for training battles')

battle_parser = api.parser()
battle_parser.add_argument('master_1', type=str, help="master 1 id", location='form', required=True)
battle_parser.add_argument('master_2', type=str, help="master 2 id", location='form', required=True)

@ns.route('/battle')

class trainning_battle(Resource):

	@api.doc(parser=battle_parser)
	@api.expect(battle_parser)
	def post(self):
		args = battle_parser.parse_args()
		self.validate(args)
		data = {'master_1': args['master_1'], 'master_2': args['master_2']}
		training_battle.delay(data)
		return {'message': 'league battle is in process'}

	def validate(self, data):
		if data['master_1'] == data['master_2']:
			api.abort(400, "you can't battle against yourself")	


@ns.route('/results')

class training_results(Resource):

	def get(self):
		result = []
		battles = db.training_battles.find()
		for battle in battles:
			winner = db.masters.find_one({'_id': ObjectId(battle['winner'])})
			loser = db.masters.find_one({'_id': ObjectId(battle['loser'])})
			result.append(
					{
					'winner': 
						{
							'id': str(winner['_id']),
							'name': winner['name']
						},
					'loser': 
						{
							'id': str(loser['_id']),
							'name': loser['name']
						}
					}
					)
		return result