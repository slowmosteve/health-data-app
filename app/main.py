import os
from flask import Flask, request
import logging
from utils import get_data, write_to_file
from gcp import upload_to_gcs

# set log level (DEBUG, INFO)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return ('Server running', 200)

@app.route('/fetch_data', methods=['GET', 'POST'])
def fetch_data():
    """This route will initiate a request for data from the Health Canada API
    """
    if request.method == 'GET':
        return ("Use this endpoint with POST method to fetch data", 200)
    elif request.method == 'POST':
        # request data
        app.logger.info("Requesting data")
        data = get_data('regulatorydecision')
        # write to file
        app.logger.info("Writing to file")
        write_to_file(data)
        # upload to cloud storage
        app.logger.info("Uploading to GCS")
        upload_to_gcs('data.json', 'health-ca-data-staging')

        return ("Fetching data", 200)

if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)