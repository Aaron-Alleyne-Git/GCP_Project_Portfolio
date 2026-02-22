# terraform/modules/pubsub-topic/main.tf
resource "google_pubsub_topic" "email_events" {
  name = "email-events-topic"
  
  message_retention_duration = "86400s" # 24 hours
}

resource "google_pubsub_subscription" "email_events_sub" {
  name  = "email-events-subscription"
  topic = google_pubsub_topic.email_events.name
  
  ack_deadline_seconds = 20
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dlq.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_topic" "dlq" {
  name = "email-events-dlq"
}