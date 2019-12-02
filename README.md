# Health Products Regulatory Data App

This project will use data from the Drug and Health Product Register API provided by the Government of Canada. Details about the API can be found here: https://health-products.canada.ca/api/documentation/summary-report-documentation-en.html

This application is largely based on the example here: https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/run/pubsub

## Discovery
- Use this endpoint to get a summary of decisions: https://health-products.canada.ca/api/summary-report/api/regulatorydecision/?lang=en&type=json
- Use this endpoint to get details on the basis of a decision https://health-products.canada.ca/api/summary-report/api/basisdecision/?lang=en&type=json
- Use this endpoint to get information about safety reviews completed by Health Canada https://health-products.canada.ca/api/summary-report/api/safetyreview/?lang=en&type=json

## Shell Scripts
- `local_server` is used to run the app locally
- `pipenv_setup` is used to run a virtual environment in order to run python functions
  - change directories to `/app` then run `sh ../bin/pipenv_setup`

## Project Overview
- One time fetch data from these endpoints and store them in Cloud Storage
  - Post route
  - Also publish message on Pub/Sub
- Load data from Cloud Storage into BigQuery
  - Post route
  - Triggered from Pub/Sub message
  - Check if data already exists
- Present data
  - Get route
  - Provide summary stats about data available
    - Number of cases
      - Dates
      - Type of submission
      - Manufacturers
      - Medical Ingredients
    - Approvals vs Denied
      - Dates
      - Type of submission
      - Manufacturers
      - Medical Ingredients

## Status
- app server in `main.py` deployed and runs locally using `local_server` shell script
- `utils.py` has functions for API call and writing to file
- `gcp.py` has function for uploading file to GCS
- updated dockerfile to use local modules

## To do
- add Pubsub message after uploading file
- add route in app server that will be subscribed to pubsub

## Setup
- create a project using `glcoud projects create [project name]`
- create a gcloud configuration using `gcloud config configurations create [project name]`
- setup config using `gcloud init`
- create a cloud storage bucket
- build container and publish on Container Registry `gcloud builds submit --tag gcr.io/[project name]/[container name]`
- deploy app `gcloud run deploy [service name] --image gcr.io/[project name]/[container name]`

