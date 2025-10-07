terraform {
  required_version = ">= 0.12"
  required_providers {
    authentik = {
      source  = "goauthentik/authentik"
      version = "2025.8.1"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.3.0"
    }
  }
}
