resource "authentik_group" "media_bazarr_users" {
  name         = "media-bazarr-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
  attributes = jsonencode({
    bazarr_username = data.sops_file.secrets.data["default_username"]
    bazarr_password = data.sops_file.secrets.data["bazarr_password"]
  })
}

resource "authentik_provider_proxy" "media_bazarr" {
  name               = "media-bazarr"
  external_host      = "https://bazarr.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
  basic_auth_enabled = true
  basic_auth_username_attribute = "bazarr_username"
  basic_auth_password_attribute = "bazarr_password"
}

resource "authentik_application" "media_bazarr" {
  name              = "Bazarr"
  slug              = "subs"
  group             = "Media"
  protocol_provider = resource.authentik_provider_proxy.media_bazarr.id
  meta_icon         = "https://styles.redditmedia.com/t5_w811i/styles/communityIcon_dkzq5urm71g21.png?width=256&s=739ac34c7a80873019a37f3108c786423ded77bc"
  meta_description  = "Subs"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "media_bazarr" {
  target = authentik_application.media_bazarr.uuid
  group  = authentik_group.media_bazarr_users.id
  order  = 0
}
