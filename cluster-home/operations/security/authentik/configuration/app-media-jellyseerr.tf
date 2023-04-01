resource "authentik_group" "media_jellyseerr_users" {
  name         = "media-jellyseerr-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
}

resource "authentik_provider_proxy" "media_jellyseerr" {
  name               = "media-jellyseerr"
  external_host      = "https://requests.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "media_jellyseerr" {
  name              = "Jellyseerr"
  slug              = "requests"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_jellyseerr.id
  meta_icon         = "https://raw.githubusercontent.com/Fallenbagel/jellyseerr/main/public/android-chrome-512x512.png"
  meta_description  = "Requests"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_jellyseerr" {
  target = authentik_application.media_jellyseerr.uuid
  group  = authentik_group.media_jellyseerr_users.id
  order  = 0
}
