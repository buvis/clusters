terraform {
  required_version = ">= 0.12"
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "3.0.1-rc6"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.1.1"
    }
  }
}
