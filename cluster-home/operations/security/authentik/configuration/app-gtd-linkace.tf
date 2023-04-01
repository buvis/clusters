resource "authentik_group" "gtd_linkace_users" {
  name         = "gtd-linkace-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "gtd_linkace" {
  name               = "gtd-linkace"
  external_host      = "https://bookmarks.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "gtd_linkace" {
  name              = "Linkace"
  slug              = "bookmarks"
  group             = "GTD"
  protocol_provider = resource.authentik_provider_proxy.gtd_linkace.id
  meta_icon         = "https://www.myqnap.org/wp-content/uploads/linkace_logo.jpg"
  meta_description  = "Bookmarks"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "gtd_linkace" {
  target = authentik_application.gtd_linkace.uuid
  group  = authentik_group.gtd_linkace_users.id
  order  = 0
}
