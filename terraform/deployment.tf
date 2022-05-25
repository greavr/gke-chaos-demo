

# ----------------------------------------------------------------------------------------------------------------------
# Data / Resource Creation
# ---------------------------------------------------------------------------------------------------------------------
data "google_container_cluster" "gke_cluster_0" {
    name = module.gke.cluster_list[var.regions[0].region].name
    location = module.gke.cluster_list[var.regions[0].region].location

    depends_on = [
      module.gke
    ]
}

data "google_container_cluster" "gke_cluster_1" {
    name = module.gke.cluster_list[var.regions[1].region].name
    location = module.gke.cluster_list[var.regions[1].region].location

    depends_on = [
      module.gke
    ]
}

data "google_container_cluster" "gke_cluster_2" {
    name = module.gke.cluster_list[var.regions[2].region].name
    location = module.gke.cluster_list[var.regions[2].region].location
    
    depends_on = [
      module.gke
    ]
}

provider "kubernetes" {
    host                   = "https://${data.google_container_cluster.gke_cluster_0.endpoint}"
    cluster_ca_certificate = base64decode("${data.google_container_cluster.gke_cluster_0.master_auth.0.cluster_ca_certificate}")
    token                  = data.google_client_config.current.access_token
    alias = "cluster1"
}

provider "kubernetes" {
    host                   = "https://${data.google_container_cluster.gke_cluster_1.endpoint}"
    cluster_ca_certificate = base64decode("${data.google_container_cluster.gke_cluster_1.master_auth.0.cluster_ca_certificate}")
    token                  = data.google_client_config.current.access_token
    alias = "cluster2"
}

provider "kubernetes" {
    host                   = "https://${data.google_container_cluster.gke_cluster_2.endpoint}"
    cluster_ca_certificate = base64decode("${data.google_container_cluster.gke_cluster_2.master_auth.0.cluster_ca_certificate}")
    token                  = data.google_client_config.current.access_token
    alias = "cluster3"
}

# ----------------------------------------------------------------------------------------------------------------------
# Deploy Manifests
# ----------------------------------------------------------------------------------------------------------------------
module "manifest_1" {
  source = "./modules/manifests"

  project_id = var.project_id
  iam_ksa = var.iam_ksa
  ksa_name = var.ksa_name
  namespace = var.k8-namespace
  gke-cluster-name = module.gke.cluster_list[var.regions[0].region].name
  gke-cluster-location = module.gke.cluster_list[var.regions[0].region].location

  providers = {
    kubernetes =  kubernetes.cluster1
  }

  depends_on = [
    module.gke
  ]
}

module "manifest_2" {
  source = "./modules/manifests"

  project_id = var.project_id
  iam_ksa = var.iam_ksa
  ksa_name = var.ksa_name
  namespace = var.k8-namespace
  gke-cluster-name = module.gke.cluster_list[var.regions[1].region].name
  gke-cluster-location = module.gke.cluster_list[var.regions[1].region].location

  providers = {
    kubernetes =  kubernetes.cluster2
  }

  depends_on = [
    module.gke
  ]
}

module "manifest_3" {
  source = "./modules/manifests"

  project_id = var.project_id
  iam_ksa = var.iam_ksa
  ksa_name = var.ksa_name
  namespace = var.k8-namespace
  gke-cluster-name = module.gke.cluster_list[var.regions[2].region].name
  gke-cluster-location = module.gke.cluster_list[var.regions[2].region].location

  providers = {
    kubernetes =  kubernetes.cluster3
  }

  depends_on = [
    module.gke
  ]
}