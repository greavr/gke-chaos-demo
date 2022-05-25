# GCP Project Name
variable "project_id" {}
variable "gke-cluster-name" {}
variable "gke-cluster-id" {}
variable "vpc-name" {}
variable "project-number" {}
variable "gke-sa" {}

variable "enable-mci" {
    default = false
}
variable "enable-mcs" {
    default = false
}

variable "enable-acm" {
    default = false
}