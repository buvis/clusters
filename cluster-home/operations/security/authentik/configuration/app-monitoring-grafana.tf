resource "authentik_group" "monitoring_grafana_users" {
  name         = "monitoring-grafana-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "monitoring_grafana" {
  name               = "monitoring-grafana"
  external_host      = "https://grafana.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "monitoring_grafana" {
  name              = "Grafana"
  slug              = "grafana"
  group             = "Monitoring"
  protocol_provider = resource.authentik_provider_proxy.monitoring_grafana.id
  meta_icon         = "https://cdn.icon-icons.com/icons2/2699/PNG/512/grafana_logo_icon_171048.png"
  meta_description  = "Grafana"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "monitoring_grafana" {
  target = authentik_application.monitoring_grafana.uuid
  group  = authentik_group.monitoring_grafana_users.id
  order  = 0
}
