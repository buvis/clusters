resource "authentik_group" "media_prowlarr_users" {
  name         = "media-prowlarr-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
  attributes = jsonencode({
    prowlarr_username = data.sops_file.secrets.data["default_username"]
    prowlarr_password = data.sops_file.secrets.data["prowlarr_password"]
  })
}

resource "authentik_provider_proxy" "media_prowlarr" {
  name               = "media-prowlarr"
  external_host      = "https://prowlarr.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "prowlarr_username"
  basic_auth_password_attribute = "prowlarr_password"
}

resource "authentik_application" "media_prowlarr" {
  name              = "Prowlarr"
  slug              = "indexer"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_prowlarr.id
  meta_icon         = "https://github.com/Prowlarr/Prowlarr/raw/develop/Logo/128.png"
  meta_description  = "Indexer"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_prowlarr" {
  target = authentik_application.media_prowlarr.uuid
  group  = authentik_group.media_prowlarr_users.id
  order  = 0
}
