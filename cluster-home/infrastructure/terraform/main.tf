terraform {
  required_version = ">= 1.5"
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.79.0"
    }
    sops = {
      source  = "carlpett/sops"
      version = "1.2.0"
    }
  }
}

provider "sops" {}

data "sops_file" "secrets" {
  source_file = "secrets.enc.json"
}
