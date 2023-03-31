resource "authentik_group" "media_lidarr_users" {
  name         = "media-lidarr-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
  attributes = jsonencode({
    lidarr_username = data.sops_file.secrets.data["default_username"]
    lidarr_password = data.sops_file.secrets.data["lidarr_password"]
  })
}

resource "authentik_provider_proxy" "media_lidarr" {
  name               = "media-lidarr"
  external_host      = "https://lidarr.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "lidarr_username"
  basic_auth_password_attribute = "lidarr_password"
}

resource "authentik_application" "media_lidarr" {
  name              = "Lidarr"
  slug              = "music"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_lidarr.id
  meta_icon         = "https://github.com/Lidarr/Lidarr/raw/develop/Logo/128.png"
  meta_description  = "Music"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_lidarr" {
  target = authentik_application.media_lidarr.uuid
  group  = authentik_group.media_lidarr_users.id
  order  = 0
}
