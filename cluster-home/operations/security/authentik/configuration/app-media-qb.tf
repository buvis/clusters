resource "authentik_group" "media_qb_users" {
  name         = "media-qb-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
}

resource "authentik_provider_proxy" "media_qb" {
  name               = "media-qb"
  external_host      = "https://qb.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "media_qb" {
  name              = "qBittorrent"
  slug              = "qb"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_qb.id
  meta_icon         = "https://patchhere.com/wp-content/uploads/2020/09/1200px-New_qBittorrent_Logo.svg-1-1024x1024.png"
  meta_description  = "Torrents"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_qb" {
  target = authentik_application.media_qb.uuid
  group  = authentik_group.media_qb_users.id
  order  = 0
}
