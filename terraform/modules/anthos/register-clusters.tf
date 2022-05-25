# ----------------------------------------------------------------------------------------------------------------------
# Register Anthos Cluster
# ----------------------------------------------------------------------------------------------------------------------
resource "google_gke_hub_membership" "anthos-register" {
  provider = google-beta
  membership_id = var.gke-cluster-name
  endpoint {
    gke_cluster {
      resource_link = "//container.googleapis.com/${var.gke-cluster-id}"
    }
  }

}