import os
import sys
import base64
from flask import Flask, request
import logging
from utils import get_data, write_to_file
from gcp import upload_to_gcs, pubsub_publish, pubsub_callback

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

        # publish message to pubsub
        app.logger.info("Publishing status message to Pubsub")
        message = "Data uploaded to GCS"
        pubsub_publish('gcs_updates', message)

        return ("Fetching data", 200)

@app.route('/bq_load', methods=['POST'])
def bq_load():
    """This route loads data from GCS into BigQuery triggered by a Pubsub message from fetch_data
    """
    envelope = request.get_json()
    if not envelope:
        message = "No Pub/Sub message received"
        print("Error: {}".format(message))
        return "Bad Request: {} \n {}".format(message, request), 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        message = "Invalid Pub/Sub message format"
        print("Error: {}".format(message))
        return "Bad Request: {}".format(message), 400

    pubsub_message = envelope['message']

    if isinstance(pubsub_message, dict) and 'data' in pubsub_message:
        message = base64.b64decode(pubsub_message['data']).decode('utf-8').strip()
        return "Received message: {}".format(message), 200

    # Flush the stdout to avoid log buffering.
    sys.stdout.flush()

    return "Done", 204

if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)