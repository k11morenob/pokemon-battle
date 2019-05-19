# pokemon-battle

### API Restful developed in Flask and MongoDB, pokemon battles with training battles and league battle. 

## Pre-requisites: 
* MongoDB instaled.

------------------------------------------------------------------------------------------

## Install and run:

* For run, download or clone the code and go into the folder
* Create a virtual env with Python 3.x and run it
* Install all dependencies with:
 ``` pip install -r requirements.txt ```
* Run Celery at background
``` celery -A app.celery worker --loglevel=info &```
* Run the api 
``` python app.py ```

#### Go to http://127.0.0.1:8010/api and there is swagger docs for more information. 
