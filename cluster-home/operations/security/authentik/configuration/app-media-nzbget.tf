resource "authentik_group" "media_nzbget_users" {
  name         = "media-nzbget-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
  attributes = jsonencode({
    nzbget_username = data.sops_file.secrets.data["default_username"]
    nzbget_password = data.sops_file.secrets.data["nzbget_password"]
  })
}

resource "authentik_provider_proxy" "media_nzbget" {
  name               = "media-nzbget"
  external_host      = "https://nzbget.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "nzbget_username"
  basic_auth_password_attribute = "nzbget_password"
}

resource "authentik_application" "media_nzbget" {
  name              = "NZBGet"
  slug              = "nzb"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_nzbget.id
  meta_icon         = "https://github.com/nzbget/nzbget/raw/develop/webui/img/favicon-256x256.png"
  meta_description  = "Usenet"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_nzbget" {
  target = authentik_application.media_nzbget.uuid
  group  = authentik_group.media_nzbget_users.id
  order  = 0
}
