output "gke-sa" {
    value = google_service_account.gke-node-sa.email
}


output "cluster_list" {
    value = google_container_cluster.gke-cluster  
}