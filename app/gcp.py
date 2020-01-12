import os
import json
import base64
import sys
import logging
from google.cloud import bigquery, pubsub, storage

logger = logging.getLogger('app.gcp')

def print_log(message):
    """Prints messages to console and logger

    Args:
        message: message to be logged and printed to console
    """
    logger.info(message)
    print(message)

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
        print_log("Uploaded file: {}".format(blob.name))
    except Exception as e:
        print_log("Exception: {}".format(e))

def gcs_to_bq(source_bucket_name, destination_bucket_name, dataset_id, table_id):
    """Loads data from Google Cloud Storage to BigQuery. Expected file format is NDJSON

    Args:
        source_bucket_name: source bucket name
        destination_bucket_name: destination bucket name
        dataset_id: BigQuery dataset ID
        table_id: BigQuery table ID
    """
    # configure BQ details
    bq_client = bigquery.Client()
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    dataset_ref = bq_client.dataset(dataset_id)

    # configure GCS details
    gcs_client = storage.Client()
    source_bucket = gcs_client.get_bucket(source_bucket_name)
    destination_bucket = gcs_client.get_bucket(destination_bucket_name)

    # list files in source bucket
    for blob in source_bucket.list_blobs():
        filename = blob.name
        print_log("found file: {}".format(filename))
        file_uri = "gs://{}/{}".format(source_bucket_name, filename)

        # load file to BQ
        load_job = bq_client.load_table_from_uri(file_uri, dataset_ref.table(table_id), job_config=job_config)
        print_log("starting job {}".format(load_job.job_id))
        load_job.result()
        destination_table = bq_client.get_table(dataset_ref.table(table_id))
        print_log("loaded {} rows to BigQuery".format(destination_table.num_rows))

        # transfer file to processed bucket
        source_blob = source_bucket.blob(filename)
        destination_blob = source_bucket.copy_blob(source_blob, destination_bucket, filename)
        print_log("Transfered file to processed bucket: {}".format(filename))

        # delete file from staging bucket
        source_blob.delete()
        print_log("Deleted file from staging bucket: {}".format(filename))

def pubsub_publish(topic_name, message_data, attribute=""):
    """Function that publishes a message to a GCP Pub/Sub topic
    Args:
        topic_name: Pub/Sub topic name
        message_data: JSON message to be published
        attribute: Additional metadata to be published (key value pairs)
    """
    pubsub_client = pubsub.PublisherClient()
    json_data = json.dumps(message_data)
    data_payload = base64.urlsafe_b64encode(bytearray(json_data, 'utf8'))
    print_log("Publishing message: {}".format(json_data))
    message_future = pubsub_client.publish(topic_name, data=data_payload, attribute=attribute)
    message_future.add_done_callback(pubsub_callback)

def pubsub_callback(message_future):
    """Return a callback with errors or an update ID upon publishing messages to Pub/Sub
    Args:
        topic_name: Pub/Sub topic name
        message_future: Pub/Sub message
    """
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        print_log("Failed to publish message. exception: {}.".format(message_future.exception()))
    else:
        print_log("Published message update id: {}".format(message_future.result()))

if __name__ == '__main__':
    # for local testing, provide the data_filename and destination_bucket_name as arguments
    data_filename = sys.argv[1]
    destination_bucket_name = sys.argv[2]
    print_log("Uploading file {} to bucket {}".format(data_filename, destination_bucket_name))
    upload_to_gcs(data_filename, destination_bucket_name)
