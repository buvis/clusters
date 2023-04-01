resource "authentik_group" "media_tdarr_users" {
  name         = "media-tdarr-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "media_tdarr" {
  name               = "media-tdarr"
  external_host      = "https://tdarr.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "media_tdarr" {
  name              = "Tdarr"
  slug              = "tdarr"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_tdarr.id
  meta_icon         = "https://i.imgur.com/M0ikBYL.png"
  meta_description  = "Transcoding"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_tdarr" {
  target = authentik_application.media_tdarr.uuid
  group  = authentik_group.media_tdarr_users.id
  order  = 0
}
