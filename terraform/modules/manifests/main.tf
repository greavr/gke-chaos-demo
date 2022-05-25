# ----------------------------------------------------------------------------------------------------------------------
# Create Name Space
# ----------------------------------------------------------------------------------------------------------------------
resource "kubernetes_namespace" "create" {
  metadata {
    name = var.namespace
  }

  provider = kubernetes
}

# ----------------------------------------------------------------------------------------------------------------------
# Create Service Account
# ----------------------------------------------------------------------------------------------------------------------
resource "kubernetes_service_account" "cluster" {
    metadata {
        name = var.ksa_name
        namespace = var.namespace
        annotations = {
          "iam.gke.io/gcp-service-account" = "${var.iam_ksa}@${var.project_id}.iam.gserviceaccount.com"
        }
    }
    depends_on = [
      kubernetes_namespace.create
    ]

    provider = kubernetes
}

# # ----------------------------------------------------------------------------------------------------------------------
# # kubernetes-manifests
# # ----------------------------------------------------------------------------------------------------------------------
data "kubectl_path_documents" "kubernetes-manifests" {
    pattern = "${path.module}/yaml/*.yaml"
    vars = {
        namespace = var.namespace
    }

    disable_template = true
}

resource "kubernetes_manifest" "deploy" {
    for_each  = toset(data.kubectl_path_documents.kubernetes-manifests.documents)

    manifest = yamldecode(each.value)
    
    depends_on = [
      kubernetes_namespace.create
    ]

    provider = kubernetes
}