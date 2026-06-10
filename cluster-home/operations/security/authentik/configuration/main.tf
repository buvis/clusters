terraform {
  required_version = ">= 0.12"
  required_providers {
    authentik = {
      source  = "goauthentik/authentik"
      version = "2026.2.1"
    }
    sops = {
      source = "carlpett/sops"
      version = "1.4.1"
    }
  }
}
