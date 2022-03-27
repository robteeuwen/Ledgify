# Ledgify

![CI to docker hub](https://github.com/robteeuwen/ledgify/actions/workflows/main.yml/badge.svg)

### Installing 
Use `pipenv install` to install dependencies and `pipenv shell` to activate the virtual environment. 

### Running 
Ledgify uses an app factory. There is a `create_app` function inside the application package (`__initi__.py`), which returns the `app` object. This function is used in `run.py` in combination with Flask's built in development server. 

- You can run the app locally by running `python run.py`
- You can also use gunicorn, for example by running `gunicorn run:app -w 2 --threads 2 -b 0.0.0.0:8000`. This will take the app object from `run.py`, but use Gunicorn to run the server, instead of the dev server. 
- You can also run this from a container. 

### Container configuration 
The dockerfile is based on a python base image and uses pipenv to do a system-wide install of the dependencies in the `Pipfile`. It then uses `gunicorn` to run the application on port `8000`. You can build an image from the dockerfile:

`docker build . -t robteeuwen/ledgify:latest`

You can technically do this without `robteeuwen`, but then you'd not be able to push it to a remote registry. Then run it (remember to expose port 8000)

`docker run -p [host-port]:8000 robteeuwen/ledgify:latest`

To push to docker hub: 

`docker push robteeuwen/ledgify:latest`

If you leave out the repository name (account name) you can't push. 

## Environment variables
We need a couple of env variables to run this app. They are stored in `.env`, which is used for running locally. The keys that need to be set can be copied from `.env_template`.

When running a container with docker from the command line, the environment variables in `.env` won't be available in the container. The easiest way to copy them into the container is by using `docker-compose` for running the container: 

`docker-compose up`

## CI/CD
source: https://docs.docker.com/language/java/configure-ci-cd/

## HEROKU 
We can deploy to heroku using the container image. Use these steps: 

`heroku container:push web -a ledgify`  
`heroku container:release web -a ledgify`

Heroku assigns a port itself, so you can't specify that in the Dockerfile. This may cause issues locally. Also, env variables need to be set using the Heroku command line. Refer to `.env` to know which variables need to be set, and set them manually using the Heroku cli. Like so: 

`heroku config:set -a ledgify ENVVARIABLE=ENVVALUE`