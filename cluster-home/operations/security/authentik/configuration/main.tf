terraform {
  required_version = ">= 0.12"
  required_providers {
    authentik = {
      source  = "goauthentik/authentik"
      version = "2024.4.2"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.0.0"
    }
  }
}
