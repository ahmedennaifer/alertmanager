## TODO:
- find grafana alternative that's compatible with firestore
- make dashboards

### Event-driven system that mocks alerts with an LLM and attemps to monitor and observe them.

![diagram](images/diagram.png)

# GCP Services: 

• [X] <img src="https://www.svgrepo.com/show/375384/cloud-scheduler.svg" width="20" height="20"> **Google Cloud Scheduler** - Triggers alert generation every minute and metrics calculation every 5 minutes. - DONE

• [X] <img src="https://api.iconify.design/logos:google-cloud-run.svg" width="20" height="20"> **Google Cloud Run (AlertGen)** - Generates 5 alerts using Gemini API with JSON schema validation and publishes the data to pub/sub. - DONE

• [X] <img src="https://www.svgrepo.com/show/375484/pubsub.svg" width="20" height="20"> **Google Pub/Sub** - Handles communication between alerts and different services. - DONE 

• [X] <img src="https://api.iconify.design/logos:google-cloud-functions.svg" width="20" height="20"> **Google Cloud Functions** - Processes incoming alerts with validation, enrichment, and storage. - DONE

• [X] <img src="https://www.svgrepo.com/show/375433/firestore.svg" width="20" height="20"> **Google Firestore** - KV Store for storing processed and enriched alert data. - DONE

• [X] <img src="https://www.svgrepo.com/show/354327/sendgrid-icon.svg" width="20" height="20"> **SendGrid** - Sends email alerts for critical and high severity issues. - DONE

• [X] <img src="https://api.iconify.design/logos:google-cloud-run.svg" width="20" height="20"> **Google Cloud Run (Metrics)** - Calculates system metrics from stored alert data. - DONE

• [ ] <img src="https://grafana.com/static/img/menu/grafana2.svg" width="20" height="20"> **Grafana** - Dashboard for monitoring. - TODO

• [ ] <img src="https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg" width="20" height="20"> **Google Gemini API** - Generation the actual alerts according to the schema in the prompt. - TODO
