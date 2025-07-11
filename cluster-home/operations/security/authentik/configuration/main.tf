terraform {
  required_version = ">= 0.12"
  required_providers {
    authentik = {
      source  = "goauthentik/authentik"
      version = "2025.6.0"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.2.1"
    }
  }
}
