provider "google" {
  project = var.project_id
  region  = var.location
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_service_account" "scheduler_sa" {
  account_id   = "scheduler-sa"
}

# Allow Cloud Scheduler service to create tokens for the scheduler service account
resource "google_service_account_iam_member" "scheduler_token_creator" {
  service_account_id = google_service_account.scheduler_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
}

# Allow your user account to impersonate the scheduler service account
resource "google_service_account_iam_member" "user_can_impersonate_scheduler" {
  service_account_id = google_service_account.scheduler_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "user:ahmedmennaifer@gmail.com"  # Replace with your actual email
}

resource "google_service_account" "alert_function_sa" {
  account_id   = "alert-function-sa"
}

# Grant Storage Object Viewer to the compute service account for Cloud Functions
resource "google_project_iam_member" "cloudfunctions_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

# Allow Cloud Build to access Artifact Registry
resource "google_project_iam_member" "cloudfunctions_artifactregistry" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

# Allow the scheduler service account to invoke the Cloud Run service
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  location = google_cloud_run_service.default.location
  project  = google_cloud_run_service.default.project
  service  = google_cloud_run_service.default.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
  depends_on = [google_cloud_run_service.default]
}

resource "google_cloud_scheduler_job" "job" {
  name       = "test-job"
  schedule   = "*/1 * * * *"
  region     = "europe-west6"
  time_zone  = "UTC"
  depends_on = [google_cloud_run_service.default, google_cloud_run_service_iam_member.scheduler_invoker]

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
  member = var.member
  role   = var.pubsub_role
}

# Allow the Cloud Run service to publish to the Pub/Sub topic
resource "google_pubsub_topic_iam_member" "cloudrun_publisher" {
  topic  = google_pubsub_topic.alerts_topic.name
  member = "serviceAccount:${google_service_account.scheduler_sa.email}"
  role   = "roles/pubsub.publisher"
}

resource "google_storage_bucket" "function_bucket" {
  name = "${var.project_id}-cloud-functions"
  location = var.location
}

data "archive_file" "function_zip" {
  type = "zip"
  output_path = "function-source.zip"
  source_dir = "../alertprocessor/"
}

resource "google_storage_bucket_object" "function_source" {
  name = "function-source-${data.archive_file.function_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.function_zip.output_path
}

resource "google_cloudfunctions_function" "process_alerts" {
  name = "process_alerts"
  runtime = "python310"
  region = var.location

  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = google_storage_bucket_object.function_source.name

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource = google_pubsub_topic.alerts_topic.id
  }

  entry_point = "process_alerts"
  service_account_email = google_service_account.alert_function_sa.email
  timeout = 540
  available_memory_mb = 128
}

# Grant the alert function service account access to the secret
resource "google_secret_manager_secret_iam_member" "llm_key_access_function" {
  secret_id = var.llm_key
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.alert_function_sa.email}"
}

# Grant the scheduler service account access to the secret (for Cloud Run)
resource "google_secret_manager_secret_iam_member" "llm_key_access_scheduler" {
  secret_id = var.llm_key
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Alternative: Grant secret access at project level (more permissive but should work)
resource "google_project_iam_member" "scheduler_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Also grant the main service account access to the secret if needed
resource "google_secret_manager_secret_iam_member" "llm_key_access_main" {
  secret_id = var.llm_key
  role      = "roles/secretmanager.secretAccessor"
  member    = var.member
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
      service_account_name = google_service_account.scheduler_sa.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_secret_manager_secret_iam_member.llm_key_access_scheduler,
    google_project_iam_member.scheduler_secret_accessor,
    google_service_account.scheduler_sa
  ]
}

resource "google_cloud_run_service_iam_member" "authenticated_access" {
  location = google_cloud_run_service.default.location
  project  = google_cloud_run_service.default.project
  service  = google_cloud_run_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"  # Change this to specific users/groups if you want more restricted access
}
