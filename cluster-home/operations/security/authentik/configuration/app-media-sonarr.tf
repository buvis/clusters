resource "authentik_group" "media_sonarr_users" {
  name         = "media-sonarr-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
  attributes = jsonencode({
    sonarr_username = data.sops_file.secrets.data["sonarr_username"]
    sonarr_password = data.sops_file.secrets.data["sonarr_password"]
  })
}

resource "authentik_provider_proxy" "media_sonarr" {
  name               = "media-sonarr"
  external_host      = "https://sonarr.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "sonarr_password"
  basic_auth_password_attribute = "sonarr_password"
}

resource "authentik_application" "media_sonarr" {
  name              = "Sonarr"
  slug              = "tv"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_sonarr.id
  meta_icon         = "https://github.com/Sonarr/Sonarr/raw/develop/Logo/128.png"
  meta_description  = "TV"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_sonarr" {
  target = authentik_application.media_sonarr.uuid
  group  = authentik_group.media_sonarr_users.id
  order  = 0
}
