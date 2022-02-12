# Ledgify

### Installing 
Use `pipenv install` to install dependencies and `pipenv shell` to activate the virtual environment. 

### Running 
Ledgify uses an app factory. There is a `create_app` function inside the application package (`__initi__.py`), which returns the `app` object. This function is used in `run.py` in combination with Flask's built in development server. 

- You can run the app locally by running `python run.py`
- You can also use gunicorn, for example by running `gunicorn run:app -w 2 --threads 2 -b 0.0.0.0:8000`. This will take the app object from `run.py`, but use Gunicorn to run the server, instead of the dev server. 
- You can also run this from a container. 

### Container configuration 
The dockerfile is based on a python base image and uses pipenv to do a system-wide install of the dependencies in the `Pipfile`. It then uses `gunicorn` to run the application on port `8000`. You can build an image from the dockerfile: 

`docker build . -t ledgify:latest`

and then run it (remember to expose port 8000)

`docker run -p [host-port]:8000 ledgify-latest`

## Environment variables
We need a couple of env variables to run this app. They are stored in `.env`, which is used for running locally. The keys that need to be set can be copied from `.env_template`. 