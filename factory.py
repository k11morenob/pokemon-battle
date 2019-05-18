from celery import Celery
from flask import Flask

def make_celery(app):

	celery = Celery(
		'pokemonBV',
		enable_utc=False,
		timezone='America/Caracas',
		broker='pyamqp://guest@localhost//'
		)
	celery.conf.update(app.config)

	class ContextTask(celery.Task):
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return self.run(*args, **kwargs)

	celery.Task = ContextTask
	return celery

def make_app():
	app = Flask(__name__)

	# Swagger documentation
	app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
	app.config.SWAGGER_UI_JSONEDITOR = True
	app.config['MONGO_DBNAME'] = 'pokemonDB'
	app.config['MONGO_URI'] = 'mongodb://localhost:27017/pokemonDB'
	return app
