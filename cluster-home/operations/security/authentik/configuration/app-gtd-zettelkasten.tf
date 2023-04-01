resource "authentik_group" "gtd_zettelkasten_users" {
  name         = "gtd-zettelkasten-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "gtd_zettelkasten" {
  name               = "gtd-zettelkasten"
  external_host      = "https://zkn.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "gtd_zettelkasten" {
  name              = "Bob's Zettelkasten"
  slug              = "zkn"
  group             = "GTD"
  protocol_provider = resource.authentik_provider_proxy.gtd_zettelkasten.id
  meta_icon         = "https://forum.zettelkasten.de/uploads/editor/rr/lpcpgexiuejl.png"
  meta_description  = "Zettelkasten"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "gtd_zettelkasten" {
  target = authentik_application.gtd_zettelkasten.uuid
  group  = authentik_group.gtd_zettelkasten_users.id
  order  = 0
}
