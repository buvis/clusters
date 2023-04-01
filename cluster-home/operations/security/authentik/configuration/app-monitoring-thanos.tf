resource "authentik_group" "monitoring_thanos_users" {
  name         = "monitoring-thanos-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "monitoring_thanos" {
  name               = "monitoring-thanos"
  external_host      = "https://thanos.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "monitoring_thanos" {
  name              = "Thanos"
  slug              = "thanos"
  group             = "Monitoring"
  protocol_provider = resource.authentik_provider_proxy.monitoring_thanos.id
  meta_icon         = "https://github.com/thanos-io/thanos/raw/main/website/static/icon-light.png"
  meta_description  = "Thanos"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "monitoring_thanos" {
  target = authentik_application.monitoring_thanos.uuid
  group  = authentik_group.monitoring_thanos_users.id
  order  = 0
}
