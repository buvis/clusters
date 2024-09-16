terraform {
  required_version = ">= 0.12"
  required_providers {
    authentik = {
      source  = "goauthentik/authentik"
      version = "2024.8.3"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.1.1"
    }
  }
}
