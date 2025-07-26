WIP

Event-driven system that mocks alerts with an LLM and attemps to monitor and observe them.

![diagram](images/diagram.png)


# Infra services

## ![Cloud Scheduler](https://cloud.google.com/images/products/scheduler.svg) Google Cloud Scheduler
Triggers alert generation every minute and metrics calculation every 5 minutes.

## ![Cloud Run](https://cloud.google.com/images/products/run.svg) Google Cloud Run (AlertGen)
Generates 5 alerts using Gemini API with JSON schema validation and publishes the data to pub/sub.

## ![Pub/Sub](https://cloud.google.com/images/products/pubsub.svg) Google Pub/Sub
Handles communication between alerts and different services.

## ![Cloud Functions](https://cloud.google.com/images/products/functions.svg) Google Cloud Functions
Processes incoming alerts with validation, enrichment, and storage.

## ![Firestore](https://cloud.google.com/images/products/firestore.svg) Google Firestore
KV Store for storing processed and enriched alert data.

## ![SendGrid](https://sendgrid.com/wp-content/themes/sgdotcom/pages/resource/brand/2016/SendGrid-Logomark.png) SendGrid
Sends email alerts for critical and high severity issues.


## ![Cloud Run](https://cloud.google.com/images/products/run.svg) Google Cloud Run (Metrics)
Calculates system metrics from stored alert data.

## ![Grafana](https://grafana.com/static/img/menu/grafana2.svg) Grafana
Dashboard for monitoring.

## ![Gemini](https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg) Google Gemini API
Generation the actual alerts according to the schema in the prompt.
