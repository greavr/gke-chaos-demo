# ----------------------------------------------------------------------------------------------------------------------
# Configure ACM
# ----------------------------------------------------------------------------------------------------------------------

resource "google_project_service" "enable-source-repo" {

    count = var.enable-acm == true ? 1 : 0

    project = var.project_id
    service = "sourcerepo.googleapis.com"
    disable_on_destroy = false
}

#https://github.com/GoogleCloudPlatform/gke-poc-toolkit/blob/main/terraform/modules/acm/acm.tf
resource "google_gke_hub_feature" "acm" {

    count = var.enable-acm == true ? 1 : 0

    project  = var.project_id
    provider = google-beta
    name = "configmanagement"
    location = "global"

    depends_on = [
        google_project_service.enable-source-repo
    ]
}

# Setup Cloud Repository
resource "google_sourcerepo_repository" "gke-poc-config-sync" {

    count = var.enable-acm == true ? 1 : 0

    name = "gke-poc-config-sync"    
    project  = var.project_id

    depends_on = [
        google_project_service.enable-source-repo
    ]
}

# Register Cluster
resource "google_gke_hub_feature_membership" "feature_member" {

    count = var.enable-acm == true ? 1 : 0

    location = "global"
    provider = google-beta

    feature = google_gke_hub_feature.acm[0].name
    membership = "projects/${var.project_id}/locations/global/memberships/${var.gke-cluster-name}"

    configmanagement {
        config_sync {
            git {
                sync_repo = google_sourcerepo_repository.gke-poc-config-sync[0].url
                policy_dir  = "/"
                sync_branch = "main"
                secret_type = "gcpserviceaccount"
                gcp_service_account_email = var.gke-sa
            }
        }
    }

    depends_on = [
        resource.google_gke_hub_feature.acm,
        google_sourcerepo_repository.gke-poc-config-sync
    ]
    
}
