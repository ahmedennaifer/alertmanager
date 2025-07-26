WIP

Event-driven system that mocks alerts with an LLM and attemps to monitor and observe them.

![diagram](images/diagram.png)


# Infrastructure

## <img src="https://raw.githubusercontent.com/AwesomeLogos/google-cloud-icons/master/docs/icons/Cloud%20Scheduler.svg" width="20" height="20"> Google Cloud Scheduler
Triggers alert generation every minute and metrics calculation every 5 minutes.

## <img src="https://raw.githubusercontent.com/AwesomeLogos/google-cloud-icons/master/docs/icons/Cloud%20Run.svg" width="20" height="20"> Google Cloud Run (AlertGen)
Generates 5 alerts using Gemini API with JSON schema validation and publishes the data to pub/sub.

## <img src="https://raw.githubusercontent.com/AwesomeLogos/google-cloud-icons/master/docs/icons/Cloud%20Pub%20Sub.svg" width="20" height="20"> Google Pub/Sub
Handles communication between alerts and different services.

## <img src="https://raw.githubusercontent.com/AwesomeLogos/google-cloud-icons/master/docs/icons/Cloud%20Functions.svg" width="20" height="20"> Google Cloud Functions
Processes incoming alerts with validation, enrichment, and storage.

## <img src="https://raw.githubusercontent.com/AwesomeLogos/google-cloud-icons/master/docs/icons/Cloud%20Firestore.svg" width="20" height="20"> Google Firestore
KV Store for storing processed and enriched alert data.

## <img src="https://www.svgrepo.com/show/354327/sendgrid-icon.svg" width="20" height="20"> SendGrid
Sends email alerts for critical and high severity issues.

## <img src="https://raw.githubusercontent.com/AwesomeLogos/google-cloud-icons/master/docs/icons/Cloud%20Run.svg" width="20" height="20"> Google Cloud Run (Metrics)
Calculates system metrics from stored alert data.

## <img src="https://grafana.com/static/img/menu/grafana2.svg" width="20" height="20"> Grafana
Dashboard for monitoring.

## ![Gemini](https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg) Google Gemini API
Generation the actual alerts according to the schema in the prompt.
