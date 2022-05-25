# ----------------------------------------------------------------------------------------------------------------------
# OUTPUTS:
# ----------------------------------------------------------------------------------------------------------------------
# Output GKE Connection String
output "gke_connection_command" {
 value = [
  for gke in module.gke.cluster_list  : format("gcloud container clusters get-credentials %s --region %s --project %s",gke.name,gke.location,var.project_id)
 ]
}