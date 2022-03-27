FROM python:3.9.1-slim

# install pipenv, copy pipfile and install requirements
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .

# install the dependencies system wide
# --ignore-pipfile prevents the lock file being updated
RUN pipenv install --deploy --system --ignore-pipfile

# copy all files to the image into /app, and enter /app
COPY . /app
WORKDIR /app

# now run the gunicorn command
#CMD ["gunicorn", "run:app", "-w", "2", "--threads", "2", "-b", "0.0.0.0:8000"]

# edit cmd for heroku
# source: https://stackoverflow.com/questions/15693192/heroku-node-js-error-web-process-failed-to-bind-to-port-within-60-seconds-of
CMD ["gunicorn", "run:app", "-w", "2", "--threads", "2"]