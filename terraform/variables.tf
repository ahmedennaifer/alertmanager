variable "project_id" {
  description = "project id"
  type        = string
}

variable "app_name" {
  description = "alertgen"
  type        = string
}


variable "location" {
  description = "location"
  type        = string
}


variable "member" {
  type = string
}

variable "llm_key" {
  type = string
}

variable "pubsub_topic" {
  type = string
}

variable "pubsub_subscriber" {
  type = string
}

variable "pubsub_role" {
  type = string
}

