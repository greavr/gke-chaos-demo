# ----------------------------------------------------------------------------------------------------------------------
# Configure Providers
# ----------------------------------------------------------------------------------------------------------------------
provider "google" {
  region        = var.regions[0].region
  project       = var.project_id
}

provider "google-beta" {
  region        = var.regions[0].region
  project       = var.project_id
}

# ----------------------------------------------------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------------------------------------------------
data "google_project" "project" {}
data "google_client_config" "current" {}

# ----------------------------------------------------------------------------------------------------------------------
# ORG Policies
# ----------------------------------------------------------------------------------------------------------------------
module "org_policy" {
  source  = "./modules/org_policy"

  project_id = var.project_id
}

# ----------------------------------------------------------------------------------------------------------------------
# Enable APIs
# ----------------------------------------------------------------------------------------------------------------------
resource "google_project_service" "enable-services" {
  for_each = toset(var.services_to_enable)

  project = var.project_id
  service = each.value
  disable_on_destroy = false
}

# ----------------------------------------------------------------------------------------------------------------------
# Configure VPC
# ----------------------------------------------------------------------------------------------------------------------
module "vpc" {
  source  = "./modules/vpc"
  project_id = var.project_id
  regions = var.regions
  vpc-name = var.vpc-name
  
  depends_on = [
    google_project_service.enable-services,
    module.org_policy
  ]
}

# ----------------------------------------------------------------------------------------------------------------------
# Configure GKE
# ----------------------------------------------------------------------------------------------------------------------
module "gke" {
  source  = "./modules/gke"

  project_id = var.project_id
  vpc-name = var.vpc-name
  regions = var.regions
  gke_service_account_roles = var.gke_service_account_roles
  gke-node-count = var.gke-node-count
  gke-node-type = var.gke-node-type
  
  depends_on = [
    module.vpc
  ]
}

# ----------------------------------------------------------------------------------------------------------------------
# Configure Anthos
# ----------------------------------------------------------------------------------------------------------------------
module "anthos" {
  source = "./modules/anthos"

  for_each = module.gke.cluster_list

  project_id = var.project_id
  gke-cluster-name = each.value.name
  gke-cluster-id = each.value.id
  vpc-name = var.vpc-name
  project-number = data.google_project.project.number
  gke-sa = module.gke.gke-sa

  enable-mci = false
  enable-mcs = false
  enable-acm = false

  depends_on = [
    module.gke
  ]
}

# ----------------------------------------------------------------------------------------------------------------------
# Configure Workload Identity
# ----------------------------------------------------------------------------------------------------------------------
module "workload-identity" {
  source = "./modules/workload-identity"

  project_id = var.project_id
  ksa_name = var.ksa_name
  iam_ksa = var.iam_ksa
  namespace = var.k8-namespace

  depends_on = [
    module.gke
  ]
}
