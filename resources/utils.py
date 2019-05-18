import requests

pokemon_url = 'https://pokeapi.co/api/v2/'

def get_pokemon(id_or_name):
	
	response = requests.get(pokemon_url + 'pokemon/' + str(id_or_name) + '/')

	print(response)

	return response.text