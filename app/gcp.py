import os
import json
import sys
import logging
from google.cloud import storage

logger = logging.getLogger("app.gcp")

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

if __name__ == "__main__":
    # for local testing, provide the data_filename and destination_bucket_name as arguments
    data_filename = sys.argv[1]
    destination_bucket_name = sys.argv[2]
    print("Uploading file {} to bucket {}".format(data_filename, destination_bucket_name))
    upload_to_gcs(data_filename, destination_bucket_name)
