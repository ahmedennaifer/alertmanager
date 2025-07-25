provider "google" {
  project = var.project_id
  region  = var.location
}

resource "google_service_account" "scheduler_sa" {
  account_id   = "scheduler-sa"
}


resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  location = google_cloud_run_service.default.location
  project  = google_cloud_run_service.default.project
  service  = google_cloud_run_service.default.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
  depends_on = [google_cloud_run_service.default,google_cloud_run_service_iam_member.scheduler_invoker]
}

resource "google_cloud_scheduler_job" "job" {
  name       = "test-job"
  schedule   = "*/1 * * * *"
  region     = "europe-west6"
  time_zone  = "UTC"
  depends_on = [google_cloud_run_service.default,google_cloud_run_service_iam_member.scheduler_invoker
]

  http_target {
    http_method = "GET"
    uri         = "${google_cloud_run_service.default.status[0].url}/generate?count=5"
    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
      audience = google_cloud_run_service.default.status[0].url
    }
  }
}


resource "google_pubsub_topic" "alerts_topic" {
  name = var.pubsub_topic
}

resource "google_pubsub_subscription" "subscriber" {
  name                 = var.pubsub_subscriber
  topic                = google_pubsub_topic.alerts_topic.name
  ack_deadline_seconds = 20
}

resource "google_pubsub_topic_iam_member" "publisher" {

  topic  = google_pubsub_topic.alerts_topic.name
  member = var.member2
  role   = var.pubsub_role
}


resource "google_secret_manager_secret_iam_member" "llm_key_access" {
  secret_id = var.llm_key
  role      = "roles/secretmanager.secretAccessor"
  member    = var.member2
}

resource "google_cloud_run_service" "default" {
  name     = var.app_name
  location = var.location

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/${var.app_name}"

        env {
          name = "GOOGLE_API_KEY"
          value_from {
            secret_key_ref {
              name = var.llm_key
              key  = "latest"
            }
          }
        }
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "TOPIC_NAME"
          value = var.pubsub_topic
        }
      }
    }
  }
}

