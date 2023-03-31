# https://registry.terraform.io/providers/goauthentik/authentik/latest/docs
provider "authentik" {
  url   = data.sops_file.secrets.data["authentik_endpoint"]
  token = data.sops_file.secrets.data["authentik_token"]
}
