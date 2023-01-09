terraform {
  required_version = ">= 0.12"
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = ">= 2.9.4"
    }
    sops = {
      source = "carlpett/sops"
      version = "0.7.2"
    }
  }
}
