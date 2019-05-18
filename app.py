from resources import app, celery
from restplus import api
from flask import Flask, Blueprint

blueprint = Blueprint('api', __name__, url_prefix='/api')

api.init_app(blueprint,version='0.1', title='Pokemon Battle Valdivia',description='Pokemon league api')

app.register_blueprint(blueprint)  

if __name__ == "__main__":
	app.run(debug=True, port=8010)