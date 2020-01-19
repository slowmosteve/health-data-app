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
- updated dockerfile to use `python:3.7-slim-buster` image instead of `python:3.7-alpine` which had issues installing Pubsub client library
- added a test route in app server which is triggered by a pubsub message

## To do
- enable pubsub to create auth tokens 
```gcloud projects add-iam-policy-binding PROJECT-ID \
     --member=serviceAccount:service-PROJECT-NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com \
     --role=roles/iam.serviceAccountTokenCreator
```
- create service account for pubsub
```gcloud iam service-accounts create cloud-run-pubsub-invoker \
     --display-name "Cloud Run Pub/Sub Invoker"
```
- give service account permission to invoke pubsub
```gcloud run services add-iam-policy-binding pubsub-tutorial \
   --member=serviceAccount:cloud-run-pubsub-invoker@PROJECT-ID.iam.gserviceaccount.com \
   --role=roles/run.invoker
```
- create topic and push to cloud run service url endpoint
```gcloud pubsub subscriptions create myRunSubscription --topic myRunTopic \
   --push-endpoint=SERVICE-URL/ \
   --push-auth-service-account=cloud-run-pubsub-invoker@PROJECT-ID.iam.gserviceaccount.com
```
- run BigQuery load in response to pubsub message
- create route for presenting data summary

## Setup
- create a project using `glcoud projects create [project id]`
- create a gcloud configuration using `gcloud config configurations create [project id]`
- setup config using `gcloud init`
- create a cloud storage bucket for storing NDJSON files
- create a bigquery dataset and table for loading data
- build container and publish on Container Registry `gcloud builds submit --tag gcr.io/[project id]/[container name]`
- deploy app `gcloud run deploy [service name] --image gcr.io/[project id]/[container name]`

## Authenticating calls
By default, unauthenticated calls are not allowed. In order to make a request to the service, you can use an approach similar to:
```
curl -H \
"Authorization: Bearer $(gcloud auth print-identity-token)" \
https://health-app-vqrdn6mxoa-ue.a.run.app
```