terraform {
  required_version = ">= 0.12"
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "3.0.1-rc8"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.2.0"
    }
  }
}
