resource "authentik_group" "radio_home_users" {
  name         = "radio-home-users"
  is_superuser = false
  users        = [authentik_user.bob.id, authentik_user.jani.id]
}

resource "authentik_provider_proxy" "radio_home" {
  name               = "radio-home"
  external_host      = "https://radio-home.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "radio_home" {
  name              = "Mopidy"
  slug              = "mopidy"
  group             = "Radio"
  protocol_provider = resource.authentik_provider_proxy.radio_home.id
  meta_icon         = "https://raw.githubusercontent.com/maschhoff/docker/master/mopidy/mopidy.png"
  meta_description  = "Radio at home"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "radio_home" {
  target = authentik_application.radio_home.uuid
  group  = authentik_group.radio_home_users.id
  order  = 0
}
