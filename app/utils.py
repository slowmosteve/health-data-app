import os
import json
import requests
import logging

logger = logging.getLogger('app.utils')

def get_data(endpoint):
    """Sends a GET request to the Health Canada API

    Args:
        endpoint: Specifies which endpoint to send the request to
            possible values:
                - "regulatorydecision"
                - "basisdecision"
                - "safetyreview"
    """
    url_base = "https://health-products.canada.ca/api/summary-report/api/"
    url_path = endpoint
    params = { 
        "lang": "en",
        "type": "json"
    }
    url = "{}{}".format(url_base, url_path)
    
    try:
        print("Requesting data for {}{}".format(url_base, url_path))
        logger.info("Requesting data for {}{}".format(url_base, url_path))
        resp = requests.get(url, params=params)
    except Exception as e:
        print("Exception: {}".format(e))
        logger.error("Exception: {}".format(e))
    else:
        print("Request status: {}".format(resp))
        logger.info("Request status: {}".format(resp))
        return resp

    # print("Response JSON: {}".format(resp.json()))

def write_to_file(response):
    """Write response JSON to file as newline delimited JSON

    Args:
        response: response object returned by get_data
    """
    try:
        filename_preprocess = "data_preprocess.json"
        with open(filename_preprocess, 'w') as outfile:
            json.dump(response.json(), outfile)

        # open preprocessed file and create list based on objects in response
        with open(filename_preprocess, 'r') as read_file:
            data = json.load(read_file)
            output = [json.dumps(record) for record in data]

        # write new file as newline delimited JSON
        filename = "data.json"
        with open(filename, 'w') as obj:
            print("Writing to file: {}".format(filename))
            logger.info("Writing to file: {}".format(filename))
            for i in output:
                obj.write(i+'\n')

        # delete preprocessed file
        if os.path.exists(filename_preprocess):
            os.remove(filename_preprocess)
            print("Deleting file: {}".format(filename_preprocess))
            logger.info("Deleting file: {}".format(filename_preprocess))
        else:
            print("{} does not exist".format(filename_preprocess))
            logger.info("{} does not exist".format(filename_preprocess))

    except Exception as e:
        print("Exception: {}".format(e))
        logger.error("Exception: {}".format(e))

if __name__ == '__main__':
    response = get_data ('regulatorydecision')
    write_to_file(response)
