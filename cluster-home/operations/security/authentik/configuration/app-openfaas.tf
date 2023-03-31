resource "authentik_user" "openfaas_api" {
  username = "openfaas-api"
  name     = "OpenFaaS-API"
  path     = "goauthentik.io/service-accounts"
  attributes = jsonencode({
    "goauthentik.io/user/token-expires" = true
    "goauthentik.io/user/service-account" = true
  })
}

resource "authentik_token" "openfaas_api" {
  identifier = "service-account-openfaas-api-password"
  user = authentik_user.openfaas_api.id
  intent = "app_password"
}

resource "authentik_group" "openfaas_users" {
  name         = "openfaas-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id, authentik_user.openfaas_api.id]
}

resource "authentik_group" "openfaas_admins" {
  name         = "openfaas-admins"
  is_superuser = false
  users        = [authentik_user.bob.id]
  attributes = jsonencode({
    openfaas_username = data.sops_file.secrets.data["openfaas_username"]
    openfaas_password = data.sops_file.secrets.data["openfaas_password"]
  })
}

resource "authentik_provider_proxy" "openfaas" {
  name               = "openfaas"
  external_host      = "https://fn.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "openfaas_username"
  basic_auth_password_attribute = "openfaas_password"
}

resource "authentik_application" "openfaas" {
  name              = "Openfaas"
  slug              = "fn"
  group             = "Openfaas"
  protocol_provider = resource.authentik_provider_proxy.openfaas.id
  meta_icon         = "https://avatars.githubusercontent.com/u/27013154?s=200&v=4"
  meta_description  = "B.U.V.I.S. Functions"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "openfaas_admins" {
  target = authentik_application.openfaas.uuid
  group  = authentik_group.openfaas_admins.id
  order  = 0
}

resource "authentik_policy_binding" "openfaas_users" {
  target = authentik_application.openfaas.uuid
  group  = authentik_group.openfaas_users.id
  order  = 1
}
