# ----------------------------------------------------------------------------------------------------------------------
# Configure MCS
# ----------------------------------------------------------------------------------------------------------------------

## Enable Multi-cluster service discovery
resource "google_gke_hub_feature" "mcs" {

    count = var.enable-mcs == true ? 1 : 0

    project  = var.project_id
    provider = google-beta
    name = "multiclusterservicediscovery"
    location = "global"

    depends_on = [
        google_gke_hub_membership.anthos-register
    ]
}


resource "google_project_iam_member" "mcs_service_account-roles" {

    count = var.enable-mcs == true ? 1 : 0

    role    = "roles/compute.networkViewer"
    member  = "serviceAccount:${var.project_id}.svc.id.goog[gke-mcs/gke-mcs-importer]"
    depends_on = [
        google_gke_hub_feature.mcs
        ]
}