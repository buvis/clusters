resource "authentik_group" "media_radarr_users" {
  name         = "media-radarr-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
  attributes = jsonencode({
    radarr_username = data.sops_file.secrets.data["default_username"]
    radarr_password = data.sops_file.secrets.data["radarr_password"]
  })
}

resource "authentik_provider_proxy" "media_radarr" {
  name               = "media-radarr"
  external_host      = "https://radarr.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "radarr_username"
  basic_auth_password_attribute = "radarr_password"
}

resource "authentik_application" "media_radarr" {
  name              = "Radarr"
  slug              = "movies"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_radarr.id
  meta_icon         = "https://github.com/Radarr/Radarr/raw/develop/Logo/128.png"
  meta_description  = "Movies"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_radarr" {
  target = authentik_application.media_radarr.uuid
  group  = authentik_group.media_radarr_users.id
  order  = 0
}
