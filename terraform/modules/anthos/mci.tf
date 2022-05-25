# ----------------------------------------------------------------------------------------------------------------------
# Configure MCI
# ----------------------------------------------------------------------------------------------------------------------

## Enable Multi-cluster Ingress(also gateway) project wide
resource "google_gke_hub_feature" "mci" {

    count = var.enable-mci == true ? 1 : 0

    provider = google-beta
    name = "multiclusteringress"
    location = "global"
    project  = var.project_id

    spec {
        multiclusteringress {
            config_membership = "projects/${var.project_id}/locations/global/memberships/${var.gke-cluster-name}"
        }
    }

    depends_on = [
        google_gke_hub_feature.mcs
    ]
}

resource "google_project_iam_member" "mci_service_account-roles" {

count = var.enable-mci == true ? 1 : 0

    role    = "roles/container.admin"
    member  = "serviceAccount:service-${var.project-number}@gcp-sa-multiclusteringress.iam.gserviceaccount.com"

    depends_on = [
        google_gke_hub_feature.mci
        ]
}

## Configure VPC firewall rules
resource "google_compute_firewall" "mci-ingress" {

    count = var.enable-mci == true ? 1 : 0

    name = "allow-glcb-backend-ingress"
    network = var.vpc-name

    allow {
        protocol = "tcp"
        ports    = ["0-65535"]
    }

    source_ranges =  ["130.211.0.0/22","35.191.0.0/16"]
}