# use lightweight alpine distribution of python
# FROM python:3.7-alpine
FROM python:3.7-slim-buster

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY app/requirements.txt .

# Install production dependencies.
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Copy local modules
COPY app/gcp.py ./
COPY app/utils.py ./

# Run the web service on container startup. 
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app

# modified to specify port and point to Flask app in app/main.py
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 app.main:app