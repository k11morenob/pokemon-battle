from factory import make_celery, make_app

app = make_app()

celery = make_celery(app)

from resources.views import *