import requests
import json
import random 

pokemon_url = 'https://pokeapi.co/api/v2/'

def get_pokemon(id_or_name):
	
	response = requests.get(pokemon_url + 'pokemon/' + str(id_or_name) + '/')

	return json.loads(response.text)

def get_pokemon_move(url):

	response = requests.get(url)

	return json.loads(response.text)

def random_pokemons(n_pokemons):

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
		pokemons.append(pokemon['name'])

	return pokemons

def get_accuracy(success_percent):
	
	if success_percent == None: return 0

	success_array = []

	for x in range(success_percent):
		success_array.append(1)

	if len(success_array) < 100:
		for x in range( 100 - len(success_array)):
			success_array.append(0)

	return random.sample(success_array, 1)[0]

def battle(masters):

	result = {'winner': None, 'loser': None}

	m1_used_pkm = 0
	m2_used_pkm = 0

	while True:

		#validate defeated pokemons 
		#if master 1 is loser
		if m1_used_pkm >= len(masters[0]['pokemons']) and m2_used_pkm < len(masters[1]['pokemons']):
			result['winner'] = str(masters[1]['_id'])
			result['loser'] = str(masters[0]['_id'])
			break

		#if master 2 is loser
		if m2_used_pkm >= len(masters[1]['pokemons']) and m1_used_pkm < len(masters[0]['pokemons']):
			result['winner'] = str(masters[0]['_id'])
			result['loser'] = str(masters[1]['_id'])
			break			

		#get the pokemons
		m1_pokemon = get_pokemon(masters[0]['pokemons'][m1_used_pkm])
		m2_pokemon = get_pokemon(masters[1]['pokemons'][m2_used_pkm])
		
		while True:
			
			m1_attack = get_pokemon_move(random.sample(m1_pokemon['moves'], 1)[0]['move']['url'])
			m2_attack = get_pokemon_move(random.sample(m2_pokemon['moves'], 1)[0]['move']['url'])

			print(m1_attack['name'],m2_attack['name'])
			#attack first master
			#find life

			for stat in m1_pokemon['stats']:

				if stat['stat']['name'] == 'hp':
					life_1 = stat['base_stat']
					break

			if life_1 <= 0:
				m1_used_pkm = m1_used_pkm + 1
				break

			#get accuracy 
			if get_accuracy(m1_attack['accuracy']) == 1:
				
				#random damage
				damage = 0
				
				if m1_attack['power'] != None:
					damage = random.randint(0, m1_attack['power'])


				for stat in m2_pokemon['stats']:

					if stat['stat']['name'] == 'hp':

						stat['base_stat'] = stat['base_stat'] - damage 



			for stat in m1_pokemon['stats']:

				if stat['stat']['name'] == 'hp':
					life_2 = stat['base_stat']
					break

			if life_2 <= 0:
				m2_used_pkm = m2_used_pkm + 1
				break
			#get accuracy 

			if get_accuracy(m2_attack['accuracy']) == 1:
				
				#random damage
				damage = 0

				if m2_attack['power'] != None:
					damage = random.randint(0, m2_attack['power'])

				for stat in m1_pokemon['stats']:

					if stat['stat']['name'] == 'hp':

						stat['base_stat'] = stat['base_stat'] - damage

	return result
