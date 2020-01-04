import os
import json
import sys
import logging
from google.cloud import storage, pubsub

logger = logging.getLogger('app.gcp')

def upload_to_gcs(data_filename, destination_bucket_name):
    """Uploads data file to Google Cloud Storage

    Args:
        data_filename: name of data file to be uploaded (newline delimited JSON format)
        destination_bucket_name: name of the GCS destination bucket
    """
    gcs_client = storage.Client()
    destination_bucket = gcs_client.get_bucket(destination_bucket_name)

    try:
        blob = destination_bucket.blob(data_filename)
        blob.upload_from_filename(data_filename)
        print("Uploaded file: {}".format(blob.name))
        logger.info("Uploaded file: {}".format(blob.name))
    except Exception as e:
        print("Exception: {}".format(e))
        logger.error("Exception: {}".format(e))

def publish_data(publisher, topic_name, message_data, attribute):
    """Function that publishes a message to a GCP Pub/Sub topic
    Args:
        publisher: Pub/Sub publisher client
        topic_name: Pub/Sub topic name
        message_data: JSON message to be published
        attribute: Additional metadata to be published (key value pairs)
    """
    json_data = json.dumps(message_data)
    data_payload = base64.urlsafe_b64encode(bytearray(json_data, 'utf8'))
    print("Publishing message: {}".format(json_data))
    logger.info("Publishing message: {}".format(json_data))
    message_future = publisher.publish(topic_name, data=data_payload, attribute=attribute)
    message_future.add_done_callback(pubsub_callback)

def pubsub_callback(message_future):
    """Return a callback with errors or an update ID upon publishing messages to Pub/Sub
    Args:
        topic_name: Pub/Sub topic name
        message_future: Pub/Sub message
    """
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        print("Failed to publish message. exception: {}.".format(message_future.exception()))
        logger.info()
    else:
        print("Published message update id: {}".format(message_future.result()))

if __name__ == '__main__':
    # for local testing, provide the data_filename and destination_bucket_name as arguments
    data_filename = sys.argv[1]
    destination_bucket_name = sys.argv[2]
    print("Uploading file {} to bucket {}".format(data_filename, destination_bucket_name))
    upload_to_gcs(data_filename, destination_bucket_name)
